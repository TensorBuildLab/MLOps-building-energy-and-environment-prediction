"""Pilot benchmark, step 3: score every agent's delivered model on the hidden period.

For each run folder data/benchmark/runs/<run_id>/ (copied from a task folder and completed by an agent):
  - runs model.predict(full.csv) in a separate process (the agent's code is not imported here);
  - scores the forecasts against the clean target on the hidden period: RMSE, MAE, skill vs persistence;
  - leakage test: for 15 random hidden-period times T, perturbs every value with a timestamp at or
    after T - 45 min and checks that the forecast for T does not change;
  - compares the agent's own expected RMSE with the RMSE it actually achieved.

Run:  python benchmarks/pilot/score.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
BENCH = REPO / "data" / "benchmark"
HIDDEN = BENCH / "hidden"
OUT = Path(__file__).resolve().parent / "results"
PY = sys.executable

RUNNER = textwrap.dedent("""
    import sys, importlib.util, pandas as pd
    folder, csv, out = sys.argv[1], sys.argv[2], sys.argv[3]
    sys.path.insert(0, folder)
    spec = importlib.util.spec_from_file_location("agent_model", folder + "/model.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    s = m.predict(csv)
    s = pd.Series(s)
    s.index = pd.DatetimeIndex(s.index)
    s.rename("forecast").to_csv(out, index_label="time")
""")


TASK_TZ = {"T1": "Europe/Copenhagen", "T2": "Asia/Singapore"}


def run_predict(folder: Path, csv: Path, out: Path, timeout: int = 900) -> pd.Series:
    r = subprocess.run([PY, "-c", RUNNER, str(folder), str(csv), str(out)], capture_output=True, text=True,
                       timeout=timeout, cwd=str(folder))
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-2000:])
    s = pd.read_csv(out, index_col="time")["forecast"]
    raw = pd.Series(s.index.astype(str))
    # The task asked for local time "as in the file". An index with offsets is read as given; an index
    # without a zone is read as the building's local time (a reasonable reading of the task, not an error).
    if raw.str.contains(r"([+-]\d\d:?\d\d|Z)$").all():
        idx = pd.to_datetime(raw, utc=True, format="mixed")
    else:
        task = folder.name.split("_")[0]
        idx = (pd.to_datetime(raw, format="mixed")
               .dt.tz_localize(TASK_TZ[task], ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC"))
    s.index = pd.DatetimeIndex(idx)
    s = s[s.index.notna()]
    return s[~s.index.duplicated(keep="first")]


def read_full(task: str) -> tuple:
    path = HIDDEN / f"{task}_full.csv"
    if task == "T1":
        df = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)
    else:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    return df, path


def perturbed_copy(task: str, df: pd.DataFrame, t_cut: pd.Timestamp, path: Path) -> None:
    """Every value at or after t_cut replaced by a large, obviously different number."""
    times = pd.to_datetime(df["timestamp"], utc=True, format="mixed")
    later = (times >= t_cut).to_numpy()
    p = df.copy()
    for c in p.columns:
        if c == "timestamp":
            continue
        v = pd.to_numeric(p.loc[later, c], errors="coerce")
        p.loc[later, c] = np.where(v.notna(), (v * 3 + 1000).astype(str), p.loc[later, c])
    if task == "T1":
        p.to_csv(path, sep=";", index=False, encoding="utf-8-sig")
    else:
        p.to_csv(path, index=False)


def score_run(folder: Path, meta: dict) -> dict:
    task = folder.name.split("_")[0]
    m = meta[task]
    row = {"run": folder.name, "task": task}
    report = {}
    if (folder / "report.json").exists():
        try:
            report = json.loads((folder / "report.json").read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            row["note"] = "report.json unreadable"
    row["expected_rmse"] = report.get("expected_rmse")
    df, full = read_full(task)
    try:
        pred = run_predict(folder, full, folder / "_score_pred.csv")
    except Exception as exc:  # the deliverable failed
        row.update({"delivered": False, "error": str(exc)[-300:]})
        return row
    row["delivered"] = True
    target = pd.read_csv(HIDDEN / f"{task}_clean_target.csv", index_col="time")["target"]
    target.index = pd.to_datetime(target.index, utc=True)
    cut = pd.Timestamp(m["cutoff"]).tz_convert("UTC")
    persistence = target.shift(4)
    pair = pd.concat({"y": target, "p": pred, "b": persistence}, axis=1)
    pair = pair[pair.index >= cut].dropna()
    err, base = pair["y"] - pair["p"], pair["y"] - pair["b"]
    rmse, brmse = float(np.sqrt((err ** 2).mean())), float(np.sqrt((base ** 2).mean()))
    row.update({"hidden_rows": len(pair), "rmse": rmse, "mae": float(err.abs().mean()),
                "persistence_rmse": brmse, "skill": 1 - rmse / brmse,
                "coverage": len(pair) / max(1, int((target.index >= cut).sum() - target[target.index >= cut].isna().sum()))})
    if row["expected_rmse"]:
        row["actual_over_expected"] = rmse / float(row["expected_rmse"])

    # Leakage test
    rng = np.random.default_rng(0)
    times = pair.index[rng.choice(len(pair), size=min(15, len(pair)), replace=False)]
    changed = 0
    for i, t in enumerate(times):
        tmp = folder / f"_leak_{i}.csv"
        perturbed_copy(task, df, t - pd.Timedelta(minutes=45), tmp)
        try:
            p2 = run_predict(folder, tmp, folder / f"_leak_{i}_pred.csv")
            a, b = pred.get(t, np.nan), p2.get(t, np.nan)
            if not (np.isfinite(a) and np.isfinite(b) and abs(a - b) <= 1e-6 * max(1.0, abs(a))):
                changed += 1
        except Exception:
            changed += 1
        finally:
            tmp.unlink(missing_ok=True)
            (folder / f"_leak_{i}_pred.csv").unlink(missing_ok=True)
    row["leak_tests"] = len(times)
    row["leak_failures"] = changed
    row["leakage"] = changed > 0
    return row


def main(only=None) -> None:
    meta = json.loads((HIDDEN / "meta.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for folder in sorted((BENCH / "runs").glob("T*_*")):
        if only and folder.name not in only:
            continue
        print("scoring", folder.name, flush=True)
        rows.append(score_run(folder, meta))
        print("  ", {k: rows[-1].get(k) for k in ("delivered", "rmse", "skill", "expected_rmse", "leakage")},
              flush=True)
        pd.DataFrame([rows[-1]]).to_csv(OUT / f"score_{folder.name}.csv", index=False)
    print("done")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
