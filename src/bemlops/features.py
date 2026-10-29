"""Model inputs built so that no future information slips in.

Two task modes:
- forecast (horizon > 0): predict the target `horizon` steps ahead. Measured
  inputs are only used up to the forecast time; inputs declared
  ``known_ahead`` (weather forecasts, schedules) may be used at the target time.
- estimate (horizon = 0): a "virtual sensor" that estimates the target from
  inputs measured at the same moment. The target itself is never an input.

Every feature records how far back in time it reaches, and ``audit`` refuses
any feature that reaches into the future.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Mapping, Optional, Tuple

import numpy as np
import pandas as pd

from .schema import ColumnSpec


class LeakageError(RuntimeError):
    """A model input would use information that is not available at prediction time."""


@dataclass
class Feature:
    name: str
    source: str
    shift: int  # steps before the target time; 0 = at the target time
    kind: str  # target_lag | target_rolling | input_lag | known_ahead | concurrent | calendar

    def to_dict(self):
        return asdict(self)


def steps_in(period: str, step: pd.Timedelta) -> int:
    return max(1, int(round(pd.Timedelta(period) / step)))


def target_shifts(horizon: int, step: pd.Timedelta, n_rows: int) -> List[int]:
    day = steps_in("1D", step)
    week = 7 * day
    shifts = {horizon, horizon + 1, horizon + 2, horizon + 3}
    if day > horizon + 3:
        shifts.add(day)  # same time yesterday
    if week > horizon and n_rows > 3 * week:
        shifts.add(week)  # same time last week
    return sorted(s for s in shifts if s < n_rows // 2)


def build_features(data: pd.DataFrame, target: str, specs: Mapping[str, ColumnSpec], horizon: int,
                   step: pd.Timedelta, target_lags: Optional[List[int]] = None,
                   include_doy: Optional[bool] = None,
                   holidays: Optional[List[str]] = None,
                   drop_constant: bool = True) -> Tuple[pd.DataFrame, pd.Series, List[Feature]]:
    """Build inputs. `target_lags` and `include_doy` default to automatic choices;
    a deployed model passes the choices it was trained with, and drop_constant=False so that an
    input which happens to be constant in a short live window is still used (not imputed)."""
    if horizon < 0:
        raise LeakageError("The horizon cannot be negative: that would forecast the past from the future.")
    y = data[target]
    cols: Dict[str, pd.Series] = {}
    feats: List[Feature] = []

    def add(name: str, values: pd.Series, source: str, shift: int, kind: str) -> None:
        cols[name] = values
        feats.append(Feature(name, source, shift, kind))

    if horizon > 0:
        lags = target_lags if target_lags is not None else target_shifts(horizon, step, len(data))
        for sh in lags:
            add(f"{target}__t-{sh}", y.shift(sh), target, sh, "target_lag")
        day = steps_in("1D", step)
        add(f"{target}__mean_1d", y.shift(horizon).rolling(day, min_periods=max(1, day // 2)).mean(),
            target, horizon, "target_rolling")

    for c, spec in specs.items():
        if c == target or c not in data.columns:
            continue
        s = data[c]
        if drop_constant and s.nunique(dropna=True) <= 1:
            continue
        if spec.known_ahead:
            add(c, s, c, 0, "known_ahead")
        elif horizon == 0:
            add(c, s, c, 0, "concurrent")
        else:
            add(f"{c}__t-{horizon}", s.shift(horizon), c, horizon, "input_lag")

    idx = data.index
    hour = idx.hour + idx.minute / 60.0
    dow = idx.day_of_week
    calendar = {
        "hour_sin": np.sin(2 * np.pi * hour / 24), "hour_cos": np.cos(2 * np.pi * hour / 24),
        "dow_sin": np.sin(2 * np.pi * dow / 7), "dow_cos": np.cos(2 * np.pi * dow / 7),
        "is_weekend": (dow >= 5).astype(float),
    }
    if holidays:
        calendar["is_holiday"] = pd.Index(idx.strftime("%Y-%m-%d")).isin(set(holidays)).astype(float)
    if include_doy is None:
        # Seasonal (day-of-year) inputs only with a full year of history; with less, they merely
        # label "which part of the record" and extrapolate badly into months never seen.
        include_doy = bool(len(idx)) and (idx[-1] - idx[0]) >= pd.Timedelta(days=365)
    if include_doy:
        doy = idx.day_of_year
        calendar["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
        calendar["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)
    for name, values in calendar.items():
        add(name, pd.Series(np.asarray(values, dtype=float), index=idx), "calendar", 0, "calendar")

    X = pd.DataFrame(cols, index=idx)
    return X, y, feats


def audit(feats: List[Feature], target: str, horizon: int) -> None:
    """Refuse any input that would not be available when the prediction is made."""
    if horizon < 0:
        raise LeakageError("The horizon cannot be negative.")
    for f in feats:
        if f.shift < 0:
            raise LeakageError(f"'{f.name}' reaches {-f.shift} steps into the future.")
        if f.source == target and horizon == 0:
            raise LeakageError(f"'{f.name}' uses the target itself in estimation mode.")
        if f.kind in ("target_lag", "target_rolling", "input_lag") and f.shift < horizon:
            raise LeakageError(f"'{f.name}' looks {f.shift} steps back, but the forecast is "
                               f"{horizon} steps ahead: it would see the future.")
        if f.kind == "concurrent" and horizon > 0:
            raise LeakageError(f"'{f.name}' uses a measured value at the target time in a forecast. "
                               f"Declare it known_ahead=True only if it truly is known in advance.")


def suspicious_inputs(X: pd.DataFrame, y: pd.Series, feats: List[Feature], target: str,
                      threshold: float = 0.995) -> List[str]:
    """Inputs (other than the target's own history) that are near-copies of the target.

    Usually a sign of a derived column that secretly contains the target.
    """
    warnings = []
    for f in feats:
        if f.source in (target, "calendar"):
            continue
        pair = pd.concat([X[f.name], y], axis=1).dropna()
        if len(pair) > 30 and pair.iloc[:, 0].std() > 0 and pair.iloc[:, 1].std() > 0:
            r = float(np.corrcoef(pair.iloc[:, 0], pair.iloc[:, 1])[0, 1])
            if abs(r) >= threshold:
                warnings.append(f"Input '{f.name}' is almost identical to the target (correlation {r:.3f}). "
                                f"Make sure it is not the target in disguise.")
    return warnings


def input_drivers(estimator, X: pd.DataFrame, y: pd.Series, feats: List[Feature], target: str, task: str,
                  random_state: int = 0, max_rows: int = 3000, n_repeats: int = 3) -> List[Dict[str, object]]:
    """How much of the model's accuracy each input carries, on the test period.

    Grouped permutation importance: all columns built from one input (its lags) are scrambled
    together with the same row permutation, and the increase in error is recorded. Shares are
    normalised to sum to one; inputs below 0.5% are not listed.
    """
    from .metrics import PRIMARY_METRIC, evaluate
    from .models import scores

    if len(X) < 30:
        return []
    if len(X) > max_rows:
        pick = np.sort(np.random.default_rng(random_state).choice(len(X), max_rows, replace=False))
        X, y = X.iloc[pick], y.iloc[pick]
    label = {}
    for f in feats:
        if f.source == "calendar":
            label[f.name] = "calendar (time of day, weekday)"
        elif f.source == target:
            label[f.name] = f"{target} (recent history)"
        else:
            label[f.name] = f.source
    groups: Dict[str, List[str]] = {}
    for c in X.columns:
        groups.setdefault(label.get(c, c), []).append(c)
    metric = PRIMARY_METRIC[task]
    base = evaluate(y, scores(estimator, X, task), task)[metric]
    rng = np.random.default_rng(random_state)
    drops = {}
    for g, cols in groups.items():
        losses = []
        for _ in range(n_repeats):
            Xp = X.copy()
            perm = rng.permutation(len(X))
            Xp[cols] = X[cols].to_numpy()[perm]
            losses.append(evaluate(y, scores(estimator, Xp, task), task)[metric] - base)
        drops[g] = max(0.0, float(np.mean(losses)))
    total = sum(drops.values())
    if total <= 0:
        return []
    shares = sorted(((g, d / total) for g, d in drops.items()), key=lambda t: -t[1])
    return [{"input": g, "share": float(v)} for g, v in shares if v >= 0.005]
