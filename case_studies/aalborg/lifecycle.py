"""MLOps lifecycle on real data: deploy, monitor monthly, retrain on drift, promote only if better.

Aalborg offices, 2023. A model trained on late February to April (heating season) goes into
production. Every month from May to December, the production model is monitored on that month;
when the drift check recommends it, a challenger is trained on all data to date and promoted
only if it passes the gates and beats the champion on data neither model has trained on.
A static model (never retrained) is scored on the same months for comparison.

Run:  python case_studies/aalborg/lifecycle.py
"""

from __future__ import annotations

import shutil
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
from bemlops.metrics import regression_metrics  # noqa: E402

OUT = HERE / "results"
WORK = aalborg.REPO / "runs" / "aalborg-lifecycle"
TASKS = [
    ("Heating:DH__power", None, "District-heating power, 1 h ahead"),
    ("RoomA:Sensor__CO2", "RoomA", "Room A CO2, 1 h ahead"),
]
FIRST_END = pd.Timestamp("2023-05-01", tz="Europe/Copenhagen")
MONTHS = pd.date_range("2023-05-01", "2023-12-01", freq="MS", tz="Europe/Copenhagen")


def month_scores(model, raw: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> dict:
    """Accuracy of `model` on [start, end), plus skill against persistence on the same rows."""
    window = raw[(raw.index >= start - pd.Timedelta(days=8)) & (raw.index < end)]
    out = model.predict(window, future=False, validate=False)
    persistence = out["actual"].shift(model.horizon)
    rows = out[(out.index >= start) & (out.index < end)].assign(persistence=persistence).dropna()
    m = regression_metrics(rows["actual"], rows["predicted"])
    b = regression_metrics(rows["actual"], rows["persistence"])
    return {"rmse": m["rmse"], "mae": m["mae"], "persistence_rmse": b["rmse"],
            "skill": 1 - m["rmse"] / b["rmse"] if b["rmse"] else np.nan, "rows": m["n"]}


def main() -> None:
    raw = aalborg.load()
    shutil.rmtree(WORK, ignore_errors=True)
    rows = []
    for target, room, label in TASKS:
        cols = dict(aalborg.SYSTEM)
        if room:
            cols.update(aalborg.room_columns(room))
        cols = {k: v for k, v in cols.items() if k in raw.columns}
        name = "lifecycle-" + target.replace(":", "-").replace("__", "-").replace("_", "").lower()
        reg = bemlops.Registry(WORK / "registry")

        first = bemlops.Project(raw[raw.index < FIRST_END], target, cols, horizon="1h", name=name,
                                intended_use=label)
        for n in aalborg.NOTES:
            first.note(n)
        first.check_data()
        first.prepare(freq="15min")
        first.fit(n_iter=4)
        v1 = reg.register(first.save_run(WORK / "runs"))
        reg.promote(name, v1["version"], reason="Initial deployment after the February-April training period.")
        static = reg.load(name, v1["version"])
        print(f"{name}: v1 deployed, gates passed={v1['gates_passed']}", flush=True)

        for start in MONTHS:
            end = start + pd.offsets.MonthBegin(1)
            prod_entry = reg.production(name)
            prod = reg.load(name)
            s_static = month_scores(static, raw, start, end)
            s_prod = month_scores(prod, raw, start, end)
            window = raw[(raw.index >= start - pd.Timedelta(days=8)) & (raw.index < end)]
            drift = prod.check_drift(window)
            row = {"task": label, "month": start.strftime("%Y-%m"), "production_version": prod_entry["version"],
                   **{f"static_{k}": v for k, v in s_static.items()},
                   **{f"production_{k}": v for k, v in s_prod.items()},
                   "drift_ratio": drift.ratio, "inputs_out_of_range": ";".join(sorted(drift.inputs_out_of_range)),
                   "data_issues": ";".join(drift.data_issues), "retrain_recommended": drift.retrain_recommended,
                   "challenger": None, "promoted": False, "challenger_error": None, "champion_error": None}
            if drift.retrain_recommended:
                history = raw[raw.index < end]
                res = bemlops.retrain(history, reg, name, WORK / "runs")
                c = res["comparison"]
                row.update({"challenger": res["challenger_version"], "promoted": res["promoted"],
                            "challenger_error": c["challenger"][c["metric"]],
                            "champion_error": c["champion"][c["metric"]],
                            "challenger_gates_passed": res["gates_passed"]})
            rows.append(row)
            print(f"  {row['month']}: static rmse {s_static['rmse']:.3g}, production v{prod_entry['version']} "
                  f"rmse {s_prod['rmse']:.3g}, drift x{drift.ratio:.2f}, retrain={drift.retrain_recommended}, "
                  f"promoted={row['promoted']}", flush=True)
        events = pd.DataFrame(reg.events(name))
        OUT.mkdir(parents=True, exist_ok=True)
        events.to_csv(OUT / f"{name}_registry_events.csv", index=False)
    pd.DataFrame(rows).to_csv(OUT / "lifecycle.csv", index=False)
    print(f"Wrote {OUT / 'lifecycle.csv'}")


if __name__ == "__main__":
    main()
