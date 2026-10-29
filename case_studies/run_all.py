"""Reproduce every case study in the paper with one command.

    python case_studies/download.py          # about 290 MB, checksums verified
    python case_studies/run_all.py           # several hours on a laptop
    python case_studies/make_results.py      # tables and figures for the paper

Each step writes its summary to case_studies/<dataset>/results/ (committed) and full run
folders to runs/ (local). Every run record names the code commit it ran on.
"""

from __future__ import annotations

import runpy
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = [
    ("robod", "ROBOD: 5 rooms x 9 targets", HERE / "robod" / "run.py", []),
    ("aalborg", "Aalborg: 6 rooms x 4 targets + building systems", HERE / "aalborg" / "run.py", []),
    ("faults", "Aalborg: fault injection (10 seeds)", HERE / "aalborg" / "faults.py", []),
    ("lifecycle", "Aalborg: deploy, monitor and retrain over 8 months", HERE / "aalborg" / "lifecycle.py", []),
    ("bdg2", "BDG2: one configuration on 40 buildings", HERE / "bdg2" / "run.py", ["40"]),
]

if __name__ == "__main__":
    only = sys.argv[1:]  # e.g. "robod bdg2": run only these steps (independent steps can run in parallel)
    for key, title, script, args in STEPS:
        if only and key not in only:
            continue
        t0 = time.time()
        print(f"\n=== {title} ===", flush=True)
        sys.argv = [str(script)] + args
        runpy.run_path(str(script), run_name="__main__")
        print(f"=== done in {(time.time() - t0) / 60:.1f} min ===", flush=True)
