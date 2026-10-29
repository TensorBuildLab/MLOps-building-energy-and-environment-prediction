"""Shared experiment code for the case studies (research code, not part of the package).

- protocol_comparison: the same model and inputs, evaluated the 2024 way (random split,
  feature selection on all data) and the strict way (time-ordered with a gap).
- inject_faults / detection_table: plant known faults in real data and check which are caught.
- unguarded_vs_guarded: train on faulty data with and without bemlops's checks; score both on
  the same clean test period.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

import bemlops
from bemlops.features import build_features, target_shifts
from bemlops.metrics import regression_metrics
from bemlops.split import time_split

RESULTS = Path(__file__).resolve().parent


def save_json(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")


def _rf(seed: int = 0) -> Pipeline:
    return Pipeline([("impute", SimpleImputer(strategy="median")),
                     ("model", RandomForestRegressor(n_estimators=150, min_samples_leaf=3, n_jobs=-1,
                                                     random_state=seed))])


# ----- 0. Running one task and summarising it ------------------------------------------
def run_task(df: pd.DataFrame, target: str, columns: Dict[str, Any], horizon, name: str, runs_dir: Path,
             notes=(), drop=(), freq: str = "15min", n_iter: int = 6, intended_use: str = "",
             accept: Dict[str, str] = None, models=None):
    """One prediction task through the full bemlops workflow. Returns (project, results, summary row).

    If the data check leaves errors unresolved, the task is reported as blocked (not silently fitted).
    """
    cols = {k: v for k, v in columns.items() if k in df.columns and k not in drop}
    p = bemlops.Project(df, target, cols, horizon=horizon, name=name, intended_use=intended_use)
    for n in notes:
        p.note(n)
    rep = p.check_data()
    for issue_id, reason in (accept or {}).items():
        if any(i.id == issue_id for i in rep.issues):
            p.accept(issue_id, reason)
    row: Dict[str, Any] = {"task": name, "target": target, "quantity": p.specs[target].quantity,
                           "task_type": p.task, "horizon": str(horizon),
                           "errors": ";".join(i.id for i in rep.errors),
                           "warnings": ";".join(i.id for i in rep.warnings)}
    blocked = p.unresolved()
    if blocked:
        row["status"] = "blocked: " + ";".join(i.id for i in blocked)
        return p, None, row
    p.prepare(freq=freq)
    r = p.fit(n_iter=n_iter, models=models)
    folder = p.save_run(runs_dir)
    record = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    row.update({
        "status": "fitted", "run": folder.name, "unit": r.task.get("unit"), "n_test": r.split["sizes"]["test"],
        "chosen": r.chosen, "baseline": r.baseline_name, "skill": r.skill,
        "gates_passed": all(g["passed"] for g in record["gates"].values()),
        "failed_gates": ";".join(k for k, g in record["gates"].items() if not g["passed"]),
        "g14_pass": (r.guideline14 or {}).get("passes"),
    })
    for k, v in r.test.items():
        row[f"test_{k}"] = v
    for k, v in r.test_baseline.items():
        row[f"base_{k}"] = v
    return p, r, row


# ----- 1. Evaluation protocol: 2024-style vs strict ---------------------------------
def _pooled(X, y, folds, seed, cols=None) -> Dict[str, float]:
    preds = pd.Series(np.nan, index=y.index)
    Xc = X if cols is None else X[cols]
    for train_idx, test_idx in folds:
        m = _rf(seed).fit(Xc.iloc[train_idx], y.iloc[train_idx])
        preds.iloc[test_idx] = m.predict(Xc.iloc[test_idx])
    return regression_metrics(y, preds)


def protocol_comparison(project: "bemlops.Project", seed: int = 0, k: int = 5) -> Dict[str, Any]:
    """Same features, same random forest; only the evaluation protocol differs.

    Cross-validation over the same rows, so the period being scored is identical:
      shuffled_cv:            k-fold with shuffled rows (what a random split does; the 2024 setting)
      shuffled_cv_selection:  plus feature selection on all rows first (the 2024 recipe)
      blocked_cv:             k contiguous blocks, with a buffer around each test block removed from
                              training (buffer = longest input look-back + horizon)
    And the deployment-realistic estimate:
      time_ordered_holdout:   train on the past, test on the last 10% after a horizon-length gap (bemlops)
    """
    from sklearn.model_selection import KFold

    h, step = project.horizon_steps, project.step
    lags = target_shifts(h, step, len(project.data)) if h > 0 else []
    X, y, feats = build_features(project.data, project.target, project.specs, h, step, target_lags=lags)
    keep = y.notna().to_numpy()
    X, y = X[keep], y[keep]
    n = len(y)
    out: Dict[str, Any] = {"rows": int(n), "features": int(X.shape[1])}

    shuffled = list(KFold(k, shuffle=True, random_state=seed).split(X))
    out["shuffled_cv"] = _pooled(X, y, shuffled, seed)

    Xf = pd.DataFrame(SimpleImputer(strategy="median").fit_transform(X), index=X.index, columns=X.columns)
    sel = SelectKBest(f_regression, k=max(3, X.shape[1] // 2)).fit(Xf, y)  # sees every row: the 2024 leak
    out["shuffled_cv_selection"] = _pooled(X, y, shuffled, seed, cols=X.columns[sel.get_support()])

    lookback = max([f["shift"] if isinstance(f, dict) else f.shift for f in feats] + [h])
    buffer = (lookback + h + 1) * step
    times = X.index
    blocked = []
    for test_idx in np.array_split(np.arange(n), k):
        t0, t1 = times[test_idx[0]], times[test_idx[-1]]
        train_mask = (times < t0 - buffer) | (times > t1 + buffer)
        blocked.append((np.flatnonzero(train_mask), test_idx))
    out["blocked_cv"] = _pooled(X, y, blocked, seed)
    out["buffer"] = str(buffer)

    sp = time_split(X.index, (0.8, 0.1, 0.1), gap=h * step)
    m = _rf(seed).fit(X[sp.train], y[sp.train])
    out["time_ordered_holdout"] = regression_metrics(y[sp.test], m.predict(X[sp.test]))
    out["optimism_ratio"] = out["blocked_cv"]["rmse"] / out["shuffled_cv"]["rmse"]
    return out


def protocol_row(dataset: str, name: str, target: str, horizon, comp: Dict[str, Any]) -> Dict[str, Any]:
    row = {"dataset": dataset, "task": name, "target": target, "horizon": str(horizon), "rows": comp["rows"],
           "optimism_ratio": comp["optimism_ratio"]}
    for key in ("shuffled_cv", "shuffled_cv_selection", "blocked_cv", "time_ordered_holdout"):
        row[f"rmse_{key}"] = comp[key]["rmse"]
        row[f"r2_{key}"] = comp[key]["r2"]
    return row


# ----- 2. Fault injection ------------------------------------------------------------
def inject_faults(raw: pd.DataFrame, specs: Dict[str, Any], target: str, temperature_col: str,
                  stuck_col: str, spike_col: str, text_col: str, seed: int = 0
                  ) -> Tuple[pd.DataFrame, List[Dict[str, str]]]:
    """Plant known faults in a copy of real (time-indexed) data. Returns the data and the ground truth."""
    rng = np.random.default_rng(seed)
    df = raw.sort_index().copy()
    n = len(df)
    truth = []
    step = pd.Series(df.index).diff().median()

    # Unit change part-way through: the last 40% of a degC temperature now arrives in degF.
    cut = int(0.6 * n)
    col = df.columns.get_loc(temperature_col)
    v = pd.to_numeric(df[temperature_col], errors="coerce").to_numpy(dtype=float, copy=True)
    v[cut:] = v[cut:] * 9 / 5 + 32
    df.iloc[:, col] = v
    truth.append({"fault": "unit change mid-series (degC to degF)", "column": temperature_col,
                  "expected": f"out_of_range:{temperature_col}|unit_mismatch:{temperature_col}"})

    # A sensor frozen for 3 days.
    per_day = int(pd.Timedelta("1D") / step)
    s0 = int(rng.integers(int(0.1 * n), int(0.5 * n)))
    col = df.columns.get_loc(stuck_col)
    df.iloc[s0:s0 + 3 * per_day, col] = df.iloc[s0, col]
    truth.append({"fault": "stuck sensor (3 days)", "column": stuck_col, "expected": f"stuck:{stuck_col}"})

    # Single-sample spikes.
    col = df.columns.get_loc(spike_col)
    vals = pd.to_numeric(df[spike_col], errors="coerce")
    spread = float(np.nanpercentile(vals, 99) - np.nanpercentile(vals, 1))
    pos = rng.choice(np.arange(5, n - 5), 10, replace=False)
    df.iloc[pos, col] = vals.iloc[pos].to_numpy() + 2.0 * spread
    truth.append({"fault": "10 single-sample spikes", "column": spike_col, "expected": f"spikes:{spike_col}"})

    # Placeholder values in the target.
    col = df.columns.get_loc(target)
    pos = rng.choice(n, 20, replace=False)
    df.iloc[pos, col] = -999.0
    truth.append({"fault": "20 placeholder values (-999)", "column": target, "expected": f"sentinel:{target}"})

    # Text in a number column.
    df[text_col] = df[text_col].astype(object)
    col = df.columns.get_loc(text_col)
    pos = rng.choice(n, 20, replace=False)
    df.iloc[pos, col] = "OFFLINE"
    truth.append({"fault": "20 'OFFLINE' text entries", "column": text_col, "expected": f"non_numeric:{text_col}"})

    # Export problems: a 12-hour outage, a day of duplicated rows, a block out of order.
    g0 = int(rng.integers(int(0.2 * n), int(0.4 * n)))
    t0 = df.index[g0]
    df = df[~((df.index >= t0) & (df.index < t0 + pd.Timedelta(hours=12)))]
    truth.append({"fault": "12-hour outage", "column": "", "expected": "index:gaps"})
    d0 = int(0.7 * len(df))
    df = pd.concat([df.iloc[:d0 + per_day], df.iloc[d0:d0 + per_day], df.iloc[d0 + per_day:]])
    truth.append({"fault": "one day of rows exported twice", "column": "", "expected": "index:duplicates"})
    b0 = int(0.45 * len(df))
    df = pd.concat([df.iloc[:b0], df.iloc[b0:b0 + 30].iloc[::-1], df.iloc[b0 + 30:]])
    truth.append({"fault": "30 rows out of order", "column": "", "expected": "index:unsorted"})
    return df, truth


def _count(issue) -> float:
    ev = issue.evidence or {}
    for k in ("n", "n_runs", "count"):
        if k in ev:
            try:
                return float(ev[k])
            except (TypeError, ValueError):
                pass
    if "values" in ev and isinstance(ev["values"], dict):
        return float(sum(ev["values"].values()))
    digits = "".join(ch if ch.isdigit() else " " for ch in issue.message).split()
    return float(digits[0]) if digits else 1.0


def detection_table(clean_report, faulty_report, truth: List[Dict[str, str]]) -> pd.DataFrame:
    """A fault counts as detected if its issue appears only after injection, or with a larger count."""
    clean = {i.id: i for i in clean_report.issues}
    faulty = {i.id: i for i in faulty_report.issues}
    rows = []
    for t in truth:
        hit, how = False, ""
        for exp in t["expected"].split("|"):
            if exp in faulty and (exp not in clean or _count(faulty[exp]) > _count(clean[exp])):
                hit, how = True, f"{exp} ({faulty[exp].severity})"
                break
        rows.append({"fault": t["fault"], "column": t["column"], "detected": hit, "as": how})
    return pd.DataFrame(rows)


# ----- 3. Training on faulty data with and without the guardrails -------------------------
def unguarded_prepare(raw: pd.DataFrame, cols: List[str], freq: str) -> pd.DataFrame:
    """What a quick script does: coerce to numbers, sort, average duplicates, resample, forward-fill."""
    d = raw[cols].apply(pd.to_numeric, errors="coerce").sort_index()
    d = d.groupby(level=0).mean().resample(freq).mean()
    return d.ffill(limit=4)


def score_on_clean_test(model_predict, clean_prepared: pd.DataFrame, target: str, test_start: pd.Timestamp):
    pred = model_predict()
    pair = pd.concat({"a": clean_prepared[target], "p": pred}, axis=1).dropna()
    pair = pair[pair.index >= test_start]
    return regression_metrics(pair["a"], pair["p"])
