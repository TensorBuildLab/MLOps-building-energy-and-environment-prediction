"""Train the Room B CO2 forecaster with bemlops (run once; predict() never retrains).

    python train.py

Writes bemlops_run/ (bemlops run record, report, model) and
bemlops_model/model.joblib (the model predict() loads).
"""
import json
import shutil
import sys
import time
from pathlib import Path

import pandas as pd
import bemlops

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model as m  # noqa: E402

TARGET = "co2_chg"
COLUMNS = {
    # Target: change of the 15-min mean CO2 over the 1 h horizon, c(T) - c(T-1h).
    "co2_chg": {"quantity": "other", "unit": "ppm", "flat_ok": True,
                "description": "15-min mean RoomB:Sensor__CO2 minus its value 1 h earlier"},
    # CO2 sensor logs on change of value with a ~50 ppm deadband: flat runs are real.
    "co2": {"quantity": "co2", "unit": "ppm", "flat_ok": True,
            "description": "RoomB:Sensor__CO2, 15-min mean"},
    "room_temp": "zone_air_temperature [degC]",
    "room_active": "occupancy_status",
    "damper": "position [%]",
    "light_on": "equipment_status",
    "window": "equipment_status",
    "supply_flow": "airflow [m3/h]",
    "oat": "outdoor_air_temperature [degC]",
}
COLUMNS.update({k: "other" for k in m.DERIVED})

NOTES = [
    "Timestamps carry +0100/+0200 offsets (DST); parsed to UTC and converted to Europe/Copenhagen.",
    "One day (2023-05-24 23:05 to 2023-05-25 23:00) was exported twice with identical values; "
    "duplicate timestamps averaged.",
    "Rows 2023-04-24 13:05-15:30 were exported in reverse order; sorted by time.",
    "12 h gap 2023-04-02 07:40-19:45 left missing (inputs forward-filled at most 1 h, target never).",
    "RoomB:Sensor__room_temperature switched from degC to degF on 2023-05-12 (values 72-83). "
    "Readings above 50 converted from degF reading by reading in the loader (causal).",
    "Outdoor temperature has 8 isolated readings of 57-73 degC; masked in the loader as impossible.",
    "CO2 has 16 placeholder readings of -999; masked. Wind speed has 'OFFLINE' text; not used.",
    "CO2 sensor reports on change of value with ~50 ppm steps, so it is flat for days when the room "
    "is empty; declared flat_ok=True rather than masking those stretches.",
    "Stuck and spike masking in prepare() disabled: both look at later readings to decide whether "
    "a reading is bad, which a live 1 h forecast cannot do; all cleaning is row-by-row in the loader.",
    "RoomB:People__amount missing 62% (absent from 2023-04-18 on); not used.",
    "Setpoints (22 / 20.5 / 23.5 degC) never change; not used. Heating, solar, lighting level and "
    "wind not used (no clear link to room CO2 at 1 h).",
    "Operation change on 2023-05-04: ventilation schedule moved from 08:00-16:15 to 05:00-21:00 "
    "(plus 23:00 night flushing) and the window is open most of the time from 2023-05-08. "
    "Derived inputs describe the fan schedule seen 24 h / 7 d earlier at the target time of day.",
    "Split fractions 0.8/0.1/0.1 instead of 0.7/0.15/0.15: with the default split the training set "
    "ends on 2023-05-03 and contains none of the summer ventilation schedule, so no model can learn "
    "it; persistence then wins validation. With 0.8/0.1/0.1 training includes ~9 days of it.",
    "Target is the 1 h change of the 15-min mean CO2 (forecast = last known 15-min mean + "
    "predicted change). Tree models on the level could not reproduce flat periods exactly; on the "
    "same split the change target gave lower RMSE. NOTE: bemlops' 'persistence' baseline for this "
    "target means 'the last hour's change repeats'; the honest baseline is zero change "
    "(= CO2 persistence), computed separately in report.json.",
    "random_forest left out: tuning it took >30 min on this (shared) machine and it did not beat "
    "ridge or gbm in a first run.",
]


def build():
    data = m.to_15min(m.add_features(m.load_clean(HERE / "train.csv")))
    p = bemlops.Project(
        data, target=TARGET, columns=COLUMNS, horizon="1h", name="roomB-co2-1h",
        intended_use="1-hour-ahead forecast of the 15-min mean CO2 (ppm) in Room B, Aalborg.")
    return p


if __name__ == "__main__":
    t0 = time.time()
    p = build()
    report = p.check_data()
    print(report)
    for n in NOTES:
        p.note(n)
    p.prepare(freq="15min", mask_stuck=False, mask_spikes=False)
    for step in p.prepare_log:
        print(step)
    res = p.fit(models=["ridge", "gbm"], n_iter=10, fractions=(0.8, 0.1, 0.1), random_state=0)
    print(res)
    print(res.validation.to_string())
    mdir = HERE / "bemlops_model"
    mdir.mkdir(exist_ok=True)
    res.model.save(mdir / "model.joblib")
    res.predictions.to_csv(mdir / "test_predictions.csv")
    res.validation.to_csv(mdir / "validation.csv", index=False)
    (mdir / "fit_summary.txt").write_text(
        str(res) + "\n\nsplit: " + json.dumps(res.split, default=str) + "\n\ntest: "
        + json.dumps(res.test, default=str) + "\nbaseline: " + json.dumps(res.test_baseline, default=str)
        + "\n\nconfig: " + json.dumps(p.config(), default=str, indent=1), encoding="utf-8")
    print("model saved to", mdir)
    out = HERE / "bemlops_run"
    if out.exists():
        shutil.rmtree(out)
    try:
        folder = p.save_run(out)
        print("run saved to", folder)
    except Exception as e:  # bemlops bug with tz-aware data spanning a DST change
        print("save_run failed:", type(e).__name__, e)
    print("elapsed", round(time.time() - t0, 1), "s")
