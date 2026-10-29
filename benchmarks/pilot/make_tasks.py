"""Pilot benchmark, step 1: build the task folders the agents see, and the hidden data they do not.

Two tasks on real data with planted faults (the same fault set as the fault-injection study):
  T1  Aalborg Room B: mean CO2 (ppm) per 15-min interval, 1 hour ahead
  T2  ROBOD Room 5 (library): chilled-water energy (kWh) per 15-min interval, 1 hour ahead

For each task the last part of the record is hidden. Agents get train.csv (raw export format,
faults included) and TASK.md. The evaluator keeps full.csv (train + hidden period, same format and
faults) and the clean target, in data/benchmark/hidden/.

Run:  python benchmarks/pilot/make_tasks.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "case_studies"))
sys.path.insert(0, str(REPO / "case_studies" / "aalborg"))
import common  # noqa: E402

BENCH = REPO / "data" / "benchmark"
HIDDEN = BENCH / "hidden"


def write_aalborg(df: pd.DataFrame, path: Path) -> None:
    """Back to the original export format: ';' separated, '#N/A', offset timestamps."""
    out = df.copy()
    ts = out.index.strftime("%Y-%m-%dT%H:%M:%S%z")
    out.insert(0, "timestamp", ts)
    out.to_csv(path, sep=";", index=False, na_rep="#N/A", encoding="utf-8-sig")


def write_robod(df: pd.DataFrame, units: dict, path: Path) -> None:
    out = df.copy()
    ts = out.index.strftime("%Y-%m-%d %H:%M %z")
    out.columns = [f"{c} [{units[c]}]" if c in units else c for c in out.columns]
    out.insert(0, "timestamp", [t[:-2] + ":" + t[-2:] for t in ts])  # +0800 -> +08:00 as in the source
    out.to_csv(path, index=False)


TASK_TEXT = """# Task {task_id}

`train.csv` in this folder is a raw trend export from a real building ({where}). It is what the
building's system produced; data quality may be imperfect.

**Goal:** a model that forecasts **{target_desc}** for each 15-minute interval, **1 hour ahead**.

**Deliverables (in this folder):**

1. `model.py` defining

   ```python
   def predict(csv_path: str) -> pandas.Series
   ```

   - `csv_path` points to a file in exactly the same format as `train.csv`, covering the training
     period plus later data.
   - Return one forecast per 15-minute interval, indexed by the interval's start time
     (a `DatetimeIndex` in the building's local time, as in the file).
   - The forecast for the interval starting at time T may only use data with timestamps before
     T - 45 minutes (that is, data up to the end of the interval one hour earlier).
   - `predict` must not retrain. Load whatever you saved. It must run in under 5 minutes.
2. `report.json` with
   - `"expected_rmse"`: your estimate of the RMSE ({unit}) on future data;
   - `"evaluation"`: how you estimated it (one or two sentences);
   - `"data_findings"`: what you found wrong or unusual in the data and what you did about it;
   {extra}

You will not see the later data. Work only inside this folder. Use the Python interpreter at
`{python}`; do not install packages.
"""


def main() -> None:
    HIDDEN.mkdir(parents=True, exist_ok=True)
    tasks = []

    # ---- T1: Aalborg Room B CO2 -------------------------------------------------------------
    import run as aalborg  # noqa: E402

    raw = aalborg.load()
    raw = raw[(raw.index >= pd.Timestamp("2023-02-27", tz="Europe/Copenhagen"))
              & (raw.index < pd.Timestamp("2023-07-01", tz="Europe/Copenhagen"))]
    cols = list({**aalborg.SYSTEM, **aalborg.room_columns("RoomB")})
    cols = [c for c in cols if c in raw.columns]
    clean = raw[cols]
    target = "RoomB:Sensor__CO2"
    faulty, truth = common.inject_faults(clean, {}, target, temperature_col="RoomB:Sensor__room_temperature",
                                         stuck_col="Ventilation:EL_meter__power",
                                         spike_col="Outdoor:Temperature_air",
                                         text_col="Outdoor:Wind__velocity", seed=101)
    cutoff = pd.Timestamp("2023-06-01", tz="Europe/Copenhagen")
    clean_target = pd.to_numeric(clean[target], errors="coerce").resample("15min").mean()
    tasks.append(("T1", faulty, cutoff, clean_target, truth, target,
                  dict(where="an office room and its building systems in Aalborg, Denmark",
                       target_desc=f"the mean of `{target}` (CO2, ppm)", unit="ppm"),
                  lambda df, p: write_aalborg(df, p)))

    # ---- T2: ROBOD Room 5 chilled-water energy ----------------------------------------------
    rpath = REPO / "data" / "raw" / "robod" / "combined_Room5.csv"
    r = pd.read_csv(rpath)
    units = {c.split(" [")[0]: c.split(" [")[1].rstrip("]") for c in r.columns if " [" in c}
    ts = pd.to_datetime(r.pop("timestamp"), format="%Y-%m-%d %H:%M %z")
    r.index = pd.DatetimeIndex(ts).tz_convert("Asia/Singapore")
    r.columns = [c.split(" [")[0] for c in r.columns]
    target2 = "chilled_water_energy"
    faulty2, truth2 = common.inject_faults(r, {}, target2, temperature_col="air_temperature",
                                           stuck_col="supply_air_flow", spike_col="dry_bulb_temp",
                                           text_col="outdoor_relative_humidity", seed=202)
    days = np.unique(r.index.normalize())
    cutoff2 = pd.Timestamp(days[int(0.8 * len(days))])
    clean_target2 = pd.to_numeric(r[target2], errors="coerce").resample("15min").sum(min_count=1)
    tasks.append(("T2", faulty2, cutoff2, clean_target2, truth2, target2,
                  dict(where="a library room in a university building in Singapore",
                       target_desc=f"the total `{target2}` (kWh) in each interval", unit="kWh"),
                  lambda df, p, u=units: write_robod(df, u, p)))

    meta = {}
    for task_id, faulty_df, cut, clean_t, truth_list, tgt, text, writer in tasks:
        folder = BENCH / "tasks" / task_id
        folder.mkdir(parents=True, exist_ok=True)
        writer(faulty_df[faulty_df.index < cut], folder / "train.csv")
        writer(faulty_df, HIDDEN / f"{task_id}_full.csv")
        clean_t.rename("target").to_csv(HIDDEN / f"{task_id}_clean_target.csv", index_label="time")
        (folder / "TASK.md").write_text(TASK_TEXT.format(task_id=task_id, python="{python}", extra="{extra}", **text),
                                        encoding="utf-8")
        meta[task_id] = {"target": tgt, "cutoff": str(cut), "unit": text["unit"], "faults": truth_list,
                         "hidden_end": str(faulty_df.index.max())}
        print(task_id, "train rows", int((faulty_df.index < cut).sum()), "hidden from", cut)
    (HIDDEN / "meta.json").write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
