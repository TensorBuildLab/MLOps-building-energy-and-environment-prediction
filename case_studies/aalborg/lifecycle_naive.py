"""Lifecycle comparison arm: retrain every month regardless of drift (naive schedule).

Complements lifecycle.py (monitored, gated retraining) and the static model. For each month from
May to December 2023, a model is trained on all data before that month with the same settings and
scored on the month, with persistence on the same rows for reference.

Run:  python case_studies/aalborg/lifecycle_naive.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import lifecycle  # noqa: E402
import run as aalborg  # noqa: E402

import bemlops  # noqa: E402

OUT = HERE / "results"
WORK = aalborg.REPO / "runs" / "aalborg-lifecycle-naive"


def main() -> None:
    raw = aalborg.load()
    rows = []
    for target, room, label in lifecycle.TASKS:
        cols = dict(aalborg.SYSTEM)
        if room:
            cols.update(aalborg.room_columns(room))
        cols = {k: v for k, v in cols.items() if k in raw.columns}
        for start in lifecycle.MONTHS:
            end = start + pd.offsets.MonthBegin(1)
            p = bemlops.Project(raw[raw.index < start], target, cols, horizon="1h", name="naive")
            p.check_data()
            p.prepare(freq="15min")
            r = p.fit(n_iter=4, backtest_blocks=0)
            s = lifecycle.month_scores(r.model, raw, start, end)
            rows.append({"task": label, "month": start.strftime("%Y-%m"), "naive_model": r.chosen,
                         **{f"naive_{k}": v for k, v in s.items()}})
            print(f"{label} {rows[-1]['month']}: naive rmse {s['rmse']:.3g} (persistence {s['persistence_rmse']:.3g})",
                  flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "lifecycle_naive.csv", index=False)
    print(f"Wrote {OUT / 'lifecycle_naive.csv'}")


if __name__ == "__main__":
    main()
