"""Re-run the chilled-water tasks of Rooms 3-5 after the dead-meter days are set to missing.

The first run of this case study trained and scored these tasks on days when the chilled-water meter
read zero while the cooling coil was in use (see run.mask_dead_chilled_water_meter). This script
re-runs only those three tasks and replaces their rows in results/summary.csv and
results/protocol_comparison.csv. The earlier rows are kept in *_before_dead_meter_mask.csv.

Run:  python case_studies/robod/rerun_dead_meter.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import common  # noqa: E402
import run  # noqa: E402

ROOMS = (3, 4, 5)


def replace_rows(path: Path, new_rows: list, key: str) -> None:
    old = pd.read_csv(path)
    new = pd.DataFrame(new_rows)
    out = pd.concat([old[~old[key].isin(new[key])], new], ignore_index=True)
    order = list(old.columns) + [c for c in new.columns if c not in old.columns]
    out = out[order]
    # keep the original task order
    rank = {t: i for i, t in enumerate(old[key])}
    out = out.sort_values(key, key=lambda s: s.map(rank).fillna(len(rank))).reset_index(drop=True)
    out.to_csv(path, index=False)


def main() -> None:
    target, horizon, drop, use = next(t for t in run.TASKS if t[0] == "chilled_water_energy")
    rows, protocol = [], []
    for room in ROOMS:
        df = run.load(room)
        days = df.attrs.get("dead_chilled_water_days", [])
        name = f"robod-room{room}-{target}-{horizon}"
        notes = run.NOTES + [f"Dead chilled-water meter: {len(days)} day(s) set to missing ({', '.join(days)})."]
        p, r, row = common.run_task(df, target, run.COLUMNS, horizon, name, run.RUNS, notes=notes, drop=drop,
                                    intended_use=use)
        row.update({"dataset": "ROBOD", "building": f"Room {room} ({run.ROOMS[room]})"})
        rows.append(row)
        print(f"{name}: {row['status']} skill={row.get('skill')} ({len(days)} dead-meter days masked)", flush=True)
        if r is not None and room in run.PROTOCOL_ROOMS:
            protocol.append(common.protocol_row("ROBOD", name, target, horizon, common.protocol_comparison(p)))
    replace_rows(run.OUT / "summary.csv", rows, "task")
    if protocol:
        replace_rows(run.OUT / "protocol_comparison.csv", protocol, "task")
    print(f"Updated {run.OUT}")


if __name__ == "__main__":
    main()
