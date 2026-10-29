"""Copy the run records behind every reported result into the repository (no data, no models).

For each task in case_studies/{robod,aalborg,bdg2}/results/summary.csv, copies run.json, report.md and
model_card.md from runs/<dataset>/<run>/ to case_studies/<dataset>/records/<run>/. Test predictions,
plots and saved models stay local: they contain or encode the measured data. Records of runs that
were superseded (the ROBOD chilled-water tasks before the dead-meter mask) go to records/superseded/.

Run:  python case_studies/publish_records.py
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "runs"
FILES = ("run.json", "report.md", "model_card.md")
SEP = r"(?:\\\\|\\|/)+"
LOCAL_PATH = re.compile(r"(?:[A-Za-z]:|/[a-z])" + SEP + "Users" + SEP + r"[^\\/\"']+" + SEP + r"(?:[^\\/\"']+" + SEP
                        + r")*?MLOPS Building Energy and Environment Prediction", re.I)


def copy_record(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        f = src / name
        if f.exists():
            text = LOCAL_PATH.sub("<repo>", f.read_text(encoding="utf-8"))
            (dst / name).write_text(text, encoding="utf-8")


def main() -> None:
    total = 0
    for ds in ("robod", "aalborg", "bdg2"):
        summary = HERE / ds / "results" / "summary.csv"
        if not summary.exists():
            continue
        out = HERE / ds / "records"
        shutil.rmtree(out, ignore_errors=True)
        for run in pd.read_csv(summary)["run"].dropna():
            src = RUNS / ds / run
            if src.exists():
                copy_record(src, out / run)
                total += 1
            else:
                print(f"missing: {src}")
        superseded = RUNS / f"{ds}_superseded"
        for src in sorted(superseded.glob("*")) if superseded.exists() else []:
            copy_record(src, out / "superseded" / src.name)
            total += 1
    print(f"Copied {total} run records.")


if __name__ == "__main__":
    main()
