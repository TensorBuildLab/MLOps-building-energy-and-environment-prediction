"""Statistical tests for the paper (run after the case studies and the pilot scoring).

1. Diebold-Mariano tests of each fitted task's model against its baseline on the test period
   (squared-error loss for numeric targets, Brier loss for yes/no targets; HAC variance with a
   Bartlett kernel and lag = max(horizon steps, 4 (n/100)^(2/9))). Writes case_studies/dm_tests.csv.
2. Pilot: every deliverable re-scored against the time-of-day profile as well as persistence, and
   paired day-block bootstrap intervals for the RMSE difference between conditions (agent + bemlops
   minus agent alone, same task and model). Writes benchmarks/pilot/results/pilot_stats.csv and
   pilot_pairs.csv.

Run:  python case_studies/stats.py
"""

from __future__ import annotations

import json
from math import erf, sqrt
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RUNS = REPO / "runs"
PILOT = REPO / "benchmarks" / "pilot"
HIDDEN = REPO / "data" / "benchmark" / "hidden"
BRUNS = REPO / "data" / "benchmark" / "runs"


def _norm_sf(z: float) -> float:
    return 0.5 * (1 - erf(z / sqrt(2)))


def diebold_mariano(loss_model: np.ndarray, loss_base: np.ndarray, lag: int) -> tuple:
    d = loss_model - loss_base
    d = d[np.isfinite(d)]
    n = len(d)
    if n < 20:
        return float("nan"), float("nan")
    lag = max(int(lag), int(4 * (n / 100) ** (2 / 9)))  # at least the Newey-West rule-of-thumb bandwidth
    dbar = d.mean()
    dc = d - dbar
    var = np.sum(dc * dc) / n
    for k in range(1, max(1, lag) + 1):
        w = 1 - k / (lag + 1)
        var += 2 * w * np.sum(dc[k:] * dc[:-k]) / n
    if var <= 0:
        return float("nan"), float("nan")
    stat = dbar / sqrt(var / n)
    return float(stat), float(2 * _norm_sf(abs(stat)))


def dm_tests() -> pd.DataFrame:
    """One test per fitted task, using the run folder each case-study summary points to."""
    rows = []
    folders = []
    for ds in ("robod", "aalborg", "bdg2"):
        f = HERE / ds / "results" / "summary.csv"
        if f.exists():
            s = pd.read_csv(f)
            folders += [RUNS / ds / r for r in s.loc[s["status"] == "fitted", "run"].dropna()]
    for folder in folders:
        rj, pred = folder / "run.json", folder / "test_predictions.csv"
        if not rj.exists() or not pred.exists():
            continue
        rec = json.loads(rj.read_text(encoding="utf-8"))
        task = rec["task"]
        base = rec["test"]["baseline"]["name"]
        p = pd.read_csv(pred)
        col = "probability" if task["task_type"] == "classification" else "predicted"
        if base not in p.columns:
            continue
        lm = (p["actual"] - p[col]) ** 2
        lb = (p["actual"] - p[base].clip(0, 1) if task["task_type"] == "classification" else p["actual"] - p[base]) ** 2
        stat, pval = diebold_mariano(lm.to_numpy(), lb.to_numpy(), int(task["horizon_steps"]) or 1)
        rows.append({"dataset": folder.parent.name, "task": rec["config"]["name"], "chosen": rec["chosen_model"]["name"],
                     "baseline": base, "skill": rec["test"]["skill"], "dm_stat": stat, "p_value": pval,
                     "model_better_p05": bool(stat < 0 and pval < 0.05) if np.isfinite(pval) else False})
    df = pd.DataFrame(rows)
    df.to_csv(HERE / "dm_tests.csv", index=False)
    return df


TASK_TZ = {"T1": "Europe/Copenhagen", "T2": "Asia/Singapore"}


def _read_pred(path: Path, task: str) -> pd.Series:
    s = pd.read_csv(path, index_col="time")["forecast"]
    raw = pd.Series(s.index.astype(str))
    if raw.str.contains(r"([+-]\d\d:?\d\d|Z)$").all():
        idx = pd.to_datetime(raw, utc=True, format="mixed")
    else:
        idx = (pd.to_datetime(raw, format="mixed")
               .dt.tz_localize(TASK_TZ[task], ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC"))
    s.index = pd.DatetimeIndex(idx)
    s = s[s.index.notna()]
    return s[~s.index.duplicated(keep="first")]


def pilot_stats(n_boot: int = 2000, seed: int = 0):
    meta = json.loads((HIDDEN / "meta.json").read_text(encoding="utf-8"))
    rows, preds = [], {}
    for folder in sorted(BRUNS.glob("T*_*")):
        f = folder / "_score_pred.csv"
        if not f.exists():
            continue
        task = folder.name.split("_")[0]
        target = pd.read_csv(HIDDEN / f"{task}_clean_target.csv", index_col="time")["target"]
        target.index = pd.to_datetime(target.index, utc=True)
        cut = pd.Timestamp(meta[task]["cutoff"]).tz_convert("UTC")
        local = target.index.tz_convert(TASK_TZ[task])
        key = pd.MultiIndex.from_arrays([(local.day_of_week >= 5).astype(int), local.hour, local.minute])
        train = target.index < cut
        prof = pd.Series(target.to_numpy()[train], index=key[train]).groupby(level=[0, 1, 2]).mean()
        profile = pd.Series(prof.reindex(key).to_numpy(), index=target.index)
        pred = _read_pred(f, task)
        pair = pd.concat({"y": target, "p": pred, "b": target.shift(4), "prof": profile}, axis=1)
        pair = pair[pair.index >= cut].dropna()
        rmse = lambda e: float(np.sqrt(np.mean(e ** 2)))  # noqa: E731
        r, rb, rp = rmse(pair.y - pair.p), rmse(pair.y - pair.b), rmse(pair.y - pair.prof)
        rows.append({"run": folder.name, "task": task, "rmse": r, "persistence_rmse": rb, "profile_rmse": rp,
                     "skill_vs_persistence": 1 - r / rb, "skill_vs_profile": 1 - r / rp,
                     "skill_vs_best_baseline": 1 - r / min(rb, rp)})
        preds[folder.name] = pair
    stats = pd.DataFrame(rows)
    stats.to_csv(PILOT / "results" / "pilot_stats.csv", index=False)

    rng = np.random.default_rng(seed)
    pairs = []
    for task in ("T1", "T2"):
        for model in ("opus", "sonnet"):
            a, c = preds.get(f"{task}_A-{model}"), preds.get(f"{task}_C-{model}")
            if a is None or c is None:
                continue
            both = pd.concat({"y": a.y, "pa": a.p, "pc": c.p}, axis=1).dropna()
            days = both.index.tz_convert(TASK_TZ[task]).normalize()
            groups = [both[days == d] for d in np.unique(days)]
            diffs = []
            for _ in range(n_boot):
                sample = pd.concat([groups[i] for i in rng.integers(0, len(groups), len(groups))])
                diffs.append(np.sqrt(np.mean((sample.y - sample.pc) ** 2)) - np.sqrt(np.mean((sample.y - sample.pa) ** 2)))
            point = np.sqrt(np.mean((both.y - both.pc) ** 2)) - np.sqrt(np.mean((both.y - both.pa) ** 2))
            lo, hi = np.percentile(diffs, [2.5, 97.5])
            pairs.append({"task": task, "model": model, "rmse_bemlops_minus_alone": float(point),
                          "ci95_low": float(lo), "ci95_high": float(hi), "days": len(groups)})
    pairs = pd.DataFrame(pairs)
    pairs.to_csv(PILOT / "results" / "pilot_pairs.csv", index=False)
    return stats, pairs


if __name__ == "__main__":
    dm = dm_tests()
    print(dm.groupby("dataset")["model_better_p05"].agg(["mean", "sum", "count"]))
    s, p = pilot_stats()
    print(s.round(3).to_string(index=False))
    print(p.round(3).to_string(index=False))
