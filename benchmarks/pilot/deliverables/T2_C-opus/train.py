"""Train the 1-h-ahead chilled-water energy model with bemlops (run once; predict() never retrains)."""
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

import bemlops
from model import HERE, TARGET, COLUMNS, PREPARE_OPTIONS, load

warnings.filterwarnings("ignore", category=FutureWarning)

t0 = time.time()
df = load(str(HERE / "train.csv"))
print(df.shape, df.index.min(), df.index.max())

p = bemlops.Project(
    df[list(COLUMNS)], target=TARGET, columns=COLUMNS, horizon="1h", name="t2-chilled-water-1h",
    intended_use="1-hour-ahead forecast of chilled-water energy per 15-min interval for a library room AHU.",
)
rep = p.check_data()
print(rep)

p.note("Loader: timestamps parsed with their +08:00 offset and kept as naive Singapore local time.")
p.note("Loader: 288 exact duplicate rows (2021-11-15/16 exported twice) dropped; a reversed block of "
       "2021-10-28 rows sorted back into order.")
p.note("Loader: -999 placeholders (17 in the target) and 'OFFLINE' text (14 in outdoor RH) set to missing.")
p.note("Loader: air_temperature switched from degC to degF on 2021-11-08 04:45 (values 79-86); readings "
       "> 55 converted from degF row by row.")
p.note("Loader: outdoor dry-bulb single-sample spikes (41-51 degC, impossible in Singapore) and a VOC "
       "spike (3922 ppb) set to missing.")
p.note("Target faults masked (5-min level, using only same-time readings): the chilled-water meter reads 0 "
       "while the AHU fan runs and the CHW valve is open (2021-09-21 to 2021-10-26 10:25: 10 operating days in this export "
       "plus a morning, 1,472 5-min readings masked in total, with short dropouts such as 2021-09-13 16:40-17:20 and 2021-11-17 after 15:35); "
       "catch-up dumps after a dropout (5-min values 13.6 and 14.4 kWh); the meter stuck at 0.4846 "
       "while the AHU was off (2021-11-03 18:40 to 2021-11-04 10:00). Masked targets stay missing.")
p.note("Target: 15-min energy = sum of the three 5-min readings, missing unless all three are valid.")
p.note("prepare(): mask_stuck and mask_spikes switched off. Both decide about a reading using later "
       "readings (a stretch is 'stuck' only once it has lasted 6 h; a spike needs the next sample), so "
       "live forecasts could change when later data arrives. The real faults are handled row-wise in "
       "the loader instead. Night-time zeros of the target and the fan are real, not stuck.")
p.note("Inputs not used: supply_air_flow and damper_position (stuck for days at 93.15 / 1942.828 / "
       "72.98 and missing for 2 weeks), offcoil_temp_setpoint (constant), wind direction, barometric "
       "pressure, sound level, VOC, PM2.5, illuminance (no physical link to the coil load that the "
       "other inputs do not already carry).")
p.note("Derived, known ahead: time of day (min), AHU schedule window 08:00-18:45, Singapore public "
       "holiday flag. Derived, measured (lagged by the horizon by bemlops): mean chilled-water energy "
       "over the last 39 valid in-schedule intervals (about one operating day), which skips weekends "
       "and gaps.")
p.note("The training export has no weekend rows; the model has never seen a weekend.")

prep = p.prepare(freq="15min", **PREPARE_OPTIONS)
for s in p.prepare_log:
    if s.get("step") != "forward_fill":
        print(s)

models = sys.argv[1].split(",") if len(sys.argv) > 1 else ["random_forest", "gbm"]
n_iter = int(sys.argv[2]) if len(sys.argv) > 2 else 12
res = p.fit(models=models, n_iter=n_iter, random_state=0)
print(res)
print("warnings:", res.warnings, res.leakage_warnings)
print("split:", res.split)
print("model train_start/end:", res.model.train_start, res.model.train_end)
folder = p.save_run(HERE / "runs")
print("saved run to", folder)
res.model.save(HERE / "model.joblib")

# fallback profile (used only if the bemlops model cannot run on a file): mean energy by time of day
y = df[TARGET]
prof = y.groupby(df.index.hour * 60 + df.index.minute).mean()
prof.to_json(HERE / "fallback_profile.json")
summary = {
    "chosen": res.chosen, "params": {k: str(v) for k, v in res.chosen_params.items()},
    "test": res.test, "test_baseline": res.test_baseline, "skill": res.skill,
    "validation": res.validation.to_dict(orient="records"), "split": {k: str(v) for k, v in res.split.items()},
    "guideline14": res.guideline14, "warnings": res.warnings, "run_folder": str(folder),
    "train_seconds": time.time() - t0,
}
(HERE / "train_summary.json").write_text(json.dumps(summary, indent=2, default=str))
print("done in", time.time() - t0)
