"""Fault injection on real data: which planted faults do the checks catch, and what do they cost
a pipeline without guardrails?

Aalborg Room A, February-June 2023. Known faults are planted in a copy of the real data (a unit
change part-way through, a stuck sensor, spikes, -999 placeholders in the target, text entries,
an outage, duplicated rows, rows out of order). Then:
  1. detection: the data check on clean vs faulty data;
  2. cost: the same random forest, same inputs, trained on the faulty data
       (a) with a quick unguarded script, (b) with bemlops (the agent fixes the one blocking error),
     and on the clean data (c), all scored against the clean target on the same test period.

Run:  python case_studies/aalborg/faults.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import common  # noqa: E402
import run as aalborg  # noqa: E402

import bemlops  # noqa: E402
from bemlops.features import build_features, target_shifts  # noqa: E402
from bemlops.metrics import regression_metrics  # noqa: E402

OUT = HERE / "results"
TARGET = "RoomA:Sensor__CO2"
TEMP = "RoomA:Sensor__room_temperature"


def rf_predictions(data: pd.DataFrame, specs, test_start: pd.Timestamp, h: int, step: pd.Timedelta) -> pd.Series:
    """Fixed random forest on leakage-safe inputs; train before test_start, predict from test_start."""
    lags = target_shifts(h, step, len(data))
    X, y, _ = build_features(data, TARGET, specs, h, step, target_lags=lags)
    train = (X.index < test_start - h * step) & y.notna().to_numpy()
    test = X.index >= test_start
    m = common._rf(0).fit(X[train], y[train])
    return pd.Series(m.predict(X[test]), index=X.index[test])


def main(seeds=range(10)) -> None:
    raw = aalborg.load()
    raw = raw[raw.index < pd.Timestamp("2023-07-01", tz="Europe/Copenhagen")]
    cols = {**aalborg.SYSTEM, **aalborg.room_columns("RoomA")}
    cols = {k: v for k, v in cols.items() if k in raw.columns}
    keep = list(cols)
    clean_raw = raw[keep]

    # (c) clean reference and the shared test period (computed once)
    clean_p = bemlops.Project(clean_raw, TARGET, cols, horizon="1h", name="faults-clean")
    clean_report = clean_p.check_data()
    clean_p.prepare(freq="15min")
    step, h = clean_p.step, clean_p.horizon_steps
    clean_target = clean_p.data[TARGET]
    test_start = clean_p.data.index[int(0.85 * len(clean_p.data))]
    reference = rf_predictions(clean_p.data, clean_p.specs, test_start, h, step)

    def score(pred):
        pair = pd.concat({"a": clean_target, "p": pred}, axis=1).dropna()
        m = regression_metrics(pair["a"], pair["p"])
        return {"rmse_ppm": m["rmse"], "mae_ppm": m["mae"], "r2": m["r2"], "rows": m["n"]}

    detections, costs, blocking = [], [], []
    costs.append({"seed": None, "pipeline": "clean data (reference)", **score(reference)})
    for seed in seeds:
        faulty_raw, truth = common.inject_faults(
            clean_raw, cols, TARGET, temperature_col=TEMP, stuck_col="Ventilation:EL_meter__power",
            spike_col="Outdoor:Temperature_air", text_col="Outdoor:Wind__velocity", seed=seed)
        faulty_p = bemlops.Project(faulty_raw, TARGET, cols, horizon="1h", name="faults-faulty")
        table = common.detection_table(clean_report, faulty_p.check_data(), truth)
        detections.append(table.assign(seed=seed))

        # (a) unguarded: coerce, sort, average duplicates, resample, forward-fill. No checks, no masking.
        ung = common.unguarded_prepare(faulty_raw, keep, "15min")
        costs.append({"seed": seed, "pipeline": "faulty data, unguarded script",
                      **score(rf_predictions(ung, clean_p.specs, test_start, h, step))})

        # (b) bemlops: the unit change is a blocking error; the agent fixes it, the rest is automatic.
        blocked = [i.id for i in faulty_p.unresolved()]
        fixed = faulty_raw.copy()
        t = pd.to_numeric(fixed[TEMP], errors="coerce")
        fixed[TEMP] = t.where(t < 50, (t - 32) * 5 / 9)  # readings above 50 are degF after the change
        faulty_p.update(data=fixed, note=f"{TEMP} switched to degF part-way through (values above 50); "
                                         f"converted those readings back to degC.")
        still = [i.id for i in faulty_p.unresolved()]
        faulty_p.prepare(freq="15min")
        costs.append({"seed": seed, "pipeline": "faulty data, bemlops",
                      **score(rf_predictions(faulty_p.data, faulty_p.specs, test_start, h, step))})
        blocking.append({"seed": seed, "blocking_before_fix": ";".join(blocked), "blocking_after_fix": ";".join(still)})
        print(f"seed {seed}: detected {int(table['detected'].sum())}/{len(table)}; blocked by {blocked}", flush=True)

    det = pd.concat(detections, ignore_index=True)
    cost = pd.DataFrame(costs)
    rate = det.groupby("fault", sort=False)["detected"].mean().rename("detection_rate").reset_index()
    summary = cost.groupby("pipeline", sort=False)[["rmse_ppm", "mae_ppm", "r2"]].agg(["mean", "std"])
    print(rate.to_string(index=False))
    print(summary.round(2).to_string())
    OUT.mkdir(parents=True, exist_ok=True)
    det.to_csv(OUT / "fault_detection.csv", index=False)
    rate.to_csv(OUT / "fault_detection_rate.csv", index=False)
    cost.to_csv(OUT / "fault_cost.csv", index=False)
    pd.DataFrame(blocking).to_csv(OUT / "fault_blocking.csv", index=False)


if __name__ == "__main__":
    main()
