"""Low-level detectors for the mess found in real BAS exports.

These functions only find problems. ``checks.py`` turns findings into
readable issues, and ``prepare.py`` decides what to do with them.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Placeholder values that controllers and historians write when a reading is missing.
SENTINELS = np.array([-999.0, -9999.0, -99999.0, 9999.0, 99999.0, -32768.0, 32767.0, 65535.0])

_BOOL_WORDS = {
    "on": 1.0, "off": 0.0, "true": 1.0, "false": 0.0, "yes": 1.0, "no": 0.0,
    "active": 1.0, "inactive": 0.0, "occupied": 1.0, "unoccupied": 0.0,
    "open": 1.0, "closed": 0.0, "run": 1.0, "stop": 0.0, "enabled": 1.0, "disabled": 0.0,
}

# "21,5" or "1.234,5": a decimal comma (European exports read without decimal=","). Never guessed.
_DECIMAL_COMMA = re.compile(r"^\s*[-+]?(?:\d{1,3}(?:\.\d{3})+|\d+),\d+(?:\D.*)?$")
_THOUSANDS = re.compile(r"^\s*[-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?(?:\D.*)?$")
# A number at the start of a string: "72.5 °F", "1,234.5 kWh", "-3e2".
_NUMBER_PREFIX = re.compile(r"^\s*([-+]?(?:\d{1,3}(?:,\d{3})+|\d+)?(?:\.\d+)?(?:[eE][-+]?\d+)?)")


@dataclass
class Coerced:
    values: pd.Series
    n_numbers_in_text: int = 0  # e.g. "72.5 F" -> 72.5
    n_words: int = 0  # e.g. "On" -> 1 for status columns
    unparseable: Counter = field(default_factory=Counter)  # e.g. {"OFFLINE": 12}
    decimal_comma: Counter = field(default_factory=Counter)  # e.g. {"21,5": 3}: not parsed, never guessed


def _parse_text(text: str, binary: bool) -> Tuple[Optional[float], str]:
    t = text.strip()
    if binary and t.lower() in _BOOL_WORDS:
        return _BOOL_WORDS[t.lower()], "word"
    if _DECIMAL_COMMA.match(t) and not _THOUSANDS.match(t):
        return None, "decimal_comma"  # "21,5" is 21.5 in much of Europe; truncating to 21 would be silent damage
    m = _NUMBER_PREFIX.match(t)
    if m and any(ch.isdigit() for ch in m.group(1)):
        try:
            return float(m.group(1).replace(",", "")), "number"
        except ValueError:
            pass
    return None, "bad"


def coerce_numeric(s: pd.Series, binary: bool = False) -> Coerced:
    """Turn a column of mixed text and numbers into floats, recording what was done."""
    if pd.api.types.is_bool_dtype(s):
        return Coerced(s.astype(float))
    if pd.api.types.is_numeric_dtype(s):
        return Coerced(s.astype(float))
    obj = s.to_numpy(dtype=object)
    out = np.array(pd.to_numeric(pd.Series(obj), errors="coerce"), dtype=float, copy=True)
    result = Coerced(pd.Series(out, index=s.index))
    text_pos = np.where(np.isnan(out) & pd.notna(obj))[0]
    parsed: Dict[str, Tuple[Optional[float], str]] = {}
    for p in text_pos:  # work by position: raw exports often repeat timestamps
        t = str(obj[p]).strip()
        if t in ("", "nan", "NaN", "None", "null", "NULL"):
            continue
        if t not in parsed:
            parsed[t] = _parse_text(t, binary)
        value, how = parsed[t]
        if how == "number":
            result.n_numbers_in_text += 1
            out[p] = value
        elif how == "word":
            result.n_words += 1
            out[p] = value
        elif how == "decimal_comma":
            result.decimal_comma[t] += 1
        else:
            result.unparseable[t] += 1
    result.values = pd.Series(out, index=s.index)
    return result


def sentinel_mask(values: pd.Series) -> pd.Series:
    return pd.Series(np.isin(values.to_numpy(dtype=float), SENTINELS), index=values.index)


def range_mask(canonical: pd.Series, bounds: Tuple[float, float]) -> pd.Series:
    """True where a value is outside the plausible range (with a 1% margin)."""
    lo, hi = bounds
    tol = 0.01 * (hi - lo) if np.isfinite(lo) and np.isfinite(hi) else 0.0
    v = canonical.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        bad = (v < lo - tol) | (v > hi + tol)
    return pd.Series(bad & np.isfinite(v), index=canonical.index)


def _gap_breaks(times: pd.Index, gap_factor: float = 3.0) -> np.ndarray:
    """For consecutive timestamps, True where the step between them is a gap (> gap_factor x typical step)."""
    if len(times) < 2:
        return np.zeros(0, dtype=bool)
    diffs = pd.Series(times[1:] - times[:-1])
    step = diffs.median()
    return np.asarray(diffs > gap_factor * step)


@dataclass
class Run:
    start: pd.Timestamp
    end: pd.Timestamp
    value: float
    n: int

    @property
    def duration(self) -> pd.Timedelta:
        return self.end - self.start


def stuck_runs(s: pd.Series, min_duration: pd.Timedelta, ignore_zero: bool) -> List[Run]:
    """Stretches where a sensor repeats exactly the same value for too long.

    ignore_zero: for quantities that idle (solar at night, equipment off), flat stretches at the
    series' floor (zero, or a small sensor offset such as 2-4 W/m2 at night) are normal and ignored.
    """
    v = s.dropna()
    if len(v) < 3:
        return []
    vals = v.to_numpy(dtype=float)
    floor = max(0.0, float(np.nanpercentile(vals, 2))) if ignore_zero else None
    times = v.index
    # A run never spans a gap in the data: equal values on Friday night and Monday
    # morning, with no rows in between, are not a stuck sensor.
    breaks = _gap_breaks(times)
    # Vectorised run-length encoding: fast even for millions of rows.
    starts = np.flatnonzero(np.r_[True, (vals[1:] != vals[:-1]) | breaks])
    ends = np.r_[starts[1:] - 1, len(vals) - 1]
    counts = ends - starts + 1
    long_enough = (times[ends] - times[starts]) >= min_duration
    sel = (counts >= 3) & np.asarray(long_enough)
    if ignore_zero:
        tol = 0.01 * (np.nanpercentile(vals, 98) - np.nanpercentile(vals, 2)) + 1e-12
        sel &= (vals[starts] != 0) & (vals[starts] > floor + tol)
    return [Run(times[a], times[b], float(vals[a]), int(c))
            for a, b, c in zip(starts[sel], ends[sel], counts[sel])]


def stuck_mask(s: pd.Series, runs: List[Run], after: pd.Timedelta = pd.Timedelta(0)) -> pd.Series:
    """Mask stuck stretches. With `after` = the detection threshold, only the part of each stretch from the
    moment it became detectable is masked: what a live system can know at that time (no look-ahead)."""
    mask = np.zeros(len(s), dtype=bool)
    if not runs:
        return pd.Series(mask, index=s.index)
    values = s.to_numpy(dtype=float)
    idx = s.index
    ordered = idx.is_monotonic_increasing
    for r in runs:
        start = r.start + after
        if ordered:
            a, b = idx.searchsorted(start, "left"), idx.searchsorted(r.end, "right")
            mask[a:b] |= values[a:b] == r.value
        else:
            mask |= np.asarray((idx >= start) & (idx <= r.end)) & (values == r.value)
    return pd.Series(mask, index=s.index)


def spike_mask(s: pd.Series, k: float = 8.0) -> pd.Series:
    """Readings far away from the readings just before them (causal: only the past is used, so live
    serving can apply exactly the same rule as training)."""
    arr = s.to_numpy(dtype=float)
    out = np.zeros(len(arr), dtype=bool)
    pos = np.where(np.isfinite(arr))[0]
    if len(pos) < 20:
        return pd.Series(out, index=s.index)
    v = pd.Series(arr[pos])
    # Compare each reading only with neighbours from the same unbroken stretch of data.
    segment = np.r_[0, np.cumsum(_gap_breaks(s.index[pos]))]
    med = v.groupby(segment).transform(lambda x: x.shift(1).rolling(4, min_periods=3).median())
    resid = (v - med).to_numpy()
    finite = np.isfinite(resid)
    if not finite.any():
        return pd.Series(out, index=s.index)
    r = resid[finite]
    scale = 1.4826 * np.median(np.abs(r - np.median(r)))
    spread = np.nanpercentile(v, 99) - np.nanpercentile(v, 1)
    threshold = max(k * scale, 0.25 * spread, 1e-9)
    hit = np.zeros(len(v), dtype=bool)
    hit[finite] = np.abs(r) > threshold
    out[pos[hit]] = True
    return pd.Series(out, index=s.index)


@dataclass
class IndexInfo:
    n_rows: int
    start: Optional[pd.Timestamp]
    end: Optional[pd.Timestamp]
    is_sorted: bool
    n_duplicates: int
    step: Optional[pd.Timedelta]
    irregular_fraction: float
    gaps: List[Tuple[pd.Timestamp, pd.Timestamp]]
    tz: Optional[str]

    @property
    def gap_time(self) -> pd.Timedelta:
        return sum((b - a for a, b in self.gaps), pd.Timedelta(0))


def analyze_index(idx: pd.DatetimeIndex, gap_factor: float = 3.0) -> IndexInfo:
    n = len(idx)
    if n == 0:
        return IndexInfo(0, None, None, True, 0, None, 0.0, [], None)
    uniq = idx.unique().sort_values()
    # Work with Timedelta objects, not raw integers: pandas may store times in s, ms, us or ns.
    diffs = pd.Series(uniq[1:] - uniq[:-1]) if len(uniq) > 1 else pd.Series([], dtype="timedelta64[ns]")
    step = pd.Timedelta(diffs.median()) if len(diffs) else None
    irregular = float((diffs != step).mean()) if len(diffs) else 0.0
    gaps = []
    if step is not None and step > pd.Timedelta(0):
        big = np.where((diffs > gap_factor * step).to_numpy())[0]
        gaps = [(uniq[i], uniq[i + 1]) for i in big]
    return IndexInfo(
        n_rows=n,
        start=uniq[0],
        end=uniq[-1],
        is_sorted=bool(idx.is_monotonic_increasing),
        n_duplicates=int(n - len(uniq)),
        step=step,
        irregular_fraction=irregular,
        gaps=gaps,
        tz=str(idx.tz) if idx.tz is not None else None,
    )
