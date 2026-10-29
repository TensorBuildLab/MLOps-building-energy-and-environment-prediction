"""Accuracy metrics, including ASHRAE Guideline 14.

CV(RMSE) and NMBE divide by the mean of the target. That suits energy and
power, but not temperatures (a 1 degC error on a 22 degC mean looks tiny)
or CO2. So each quantity has a headline metric: CV(RMSE) for energy-like
targets, MAE in physical units for indoor-environment targets.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd

# ASHRAE Guideline 14-2014 calibration criteria, in percent.
GUIDELINE14 = {
    "hourly": {"cvrmse": 30.0, "nmbe": 10.0},
    "monthly": {"cvrmse": 15.0, "nmbe": 5.0},
}


def regression_metrics(y_true, y_pred, n_params: int = 1) -> Dict[str, float]:
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(y_pred, dtype=float)
    ok = np.isfinite(y) & np.isfinite(p)
    y, p = y[ok], p[ok]
    n = len(y)
    if n == 0:
        return {"n": 0}
    err = y - p
    rmse = float(np.sqrt(np.mean(err ** 2)))
    mean_y = float(np.mean(y))
    ss_tot = float(np.sum((y - mean_y) ** 2))
    out = {
        "n": n,
        "rmse": rmse,
        "mae": float(np.mean(np.abs(err))),
        "r2": float(1 - np.sum(err ** 2) / ss_tot) if ss_tot > 0 else float("nan"),
        "mean_actual": mean_y,
    }
    if abs(mean_y) > 1e-9:
        dof = max(n - n_params, 1)
        # |mean| so that CV(RMSE) stays a positive error measure even for net (negative-mean) meters.
        out["cvrmse_pct"] = float(100 * np.sqrt(np.sum(err ** 2) / dof) / abs(mean_y))
        out["nmbe_pct"] = float(100 * np.sum(err) / (dof * abs(mean_y)))
    return out


def classification_metrics(y_true, prob) -> Dict[str, float]:
    """For yes/no targets (occupied, equipment on). `prob` is the predicted probability of 1."""
    y = np.asarray(y_true, dtype=float)
    p = np.asarray(prob, dtype=float)
    ok = np.isfinite(y) & np.isfinite(p)
    y, p = y[ok], np.clip(p[ok], 0.0, 1.0)
    n = len(y)
    if n == 0:
        return {"n": 0}
    pred = (p >= 0.5).astype(float)
    tp = float(np.sum((pred == 1) & (y == 1)))
    fp = float(np.sum((pred == 1) & (y == 0)))
    fn = float(np.sum((pred == 0) & (y == 1)))
    tn = float(np.sum((pred == 0) & (y == 0)))
    recall_1 = tp / (tp + fn) if tp + fn else float("nan")
    recall_0 = tn / (tn + fp) if tn + fp else float("nan")
    precision = tp / (tp + fp) if tp + fp else float("nan")
    if tp == 0 and (fp + fn) > 0:
        f1 = 0.0
    elif precision + recall_1 and np.isfinite(precision + recall_1):
        f1 = float(2 * precision * recall_1 / (precision + recall_1))
    else:
        f1 = float("nan")
    out = {
        "n": n,
        "brier": float(np.mean((p - y) ** 2)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(np.nanmean([recall_1, recall_0])),
        "f1": f1,
        "share_of_ones": float(np.mean(y)),
    }
    if 0 < y.sum() < n:  # ROC AUC via the rank-sum formula, ties counted half
        ranks = pd.Series(p).rank(method="average").to_numpy()
        n1 = y.sum()
        out["roc_auc"] = float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * (n - n1)))
    return out


PRIMARY_METRIC = {"regression": "rmse", "classification": "brier"}


def evaluate(y_true, scores, task: str) -> Dict[str, float]:
    return classification_metrics(y_true, scores) if task == "classification" else regression_metrics(y_true, scores)


def skill_score(model_error: float, baseline_error: float) -> float:
    """1 = perfect, 0 = no better than the baseline, negative = worse.

    Uses RMSE for numeric targets and the Brier score for yes/no targets
    (the latter is the standard Brier skill score).
    """
    if not baseline_error or not np.isfinite(baseline_error):
        return float("nan")
    return float(1 - model_error / baseline_error)


def guideline14(actual: pd.Series, predicted: pd.Series, aggregate: str = "mean",
                resolution: str = "hourly") -> Optional[Dict[str, object]]:
    """Check the Guideline 14 hourly criteria on hourly-aggregated values."""
    pair = pd.concat({"a": actual, "p": predicted}, axis=1).dropna()
    if pair.empty:
        return None
    rule = "1h" if resolution == "hourly" else "MS"
    grouped = pair.resample(rule)
    hourly = grouped.sum(min_count=1) if aggregate == "sum" else grouped.mean()
    hourly = hourly.dropna()
    m = regression_metrics(hourly["a"], hourly["p"])
    limits = GUIDELINE14[resolution]
    if "cvrmse_pct" not in m or m["mean_actual"] <= 0:
        # The criteria assume consumption (a positive mean). They cannot be met by a net meter or a
        # near-zero series, and "not applicable" must not count as a pass.
        return {"resolution": resolution, "cvrmse_pct": m.get("cvrmse_pct", float("nan")),
                "nmbe_pct": m.get("nmbe_pct", float("nan")), "cvrmse_limit": limits["cvrmse"],
                "nmbe_limit": limits["nmbe"], "passes": False,
                "note": "not defined for a non-positive mean"}
    return {
        "resolution": resolution,
        "cvrmse_pct": m["cvrmse_pct"],
        "nmbe_pct": m["nmbe_pct"],
        "cvrmse_limit": limits["cvrmse"],
        "nmbe_limit": limits["nmbe"],
        "passes": bool(m["cvrmse_pct"] <= limits["cvrmse"] and abs(m["nmbe_pct"]) <= limits["nmbe"]),
    }
