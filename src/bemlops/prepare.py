"""Standard preparation of building data, with every step logged.

Run your own custom cleaning first if the data needs it. This step then makes
the data regular and safe to model:

1. sort by time, turn text into numbers, average duplicate timestamps
2. convert every column to its canonical unit (degC, kW, ppm, ...)
3. treat placeholder values, impossible readings, stuck stretches and spikes as missing
4. resample to a regular time grid
5. forward-fill short gaps in the inputs only

Gaps are filled forward only (never by interpolation), because a live
system cannot see the future. The target is never filled.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping, Optional, Tuple

import numpy as np
import pandas as pd

from .checks import fmt_td
from .cleaning import analyze_index, coerce_numeric, range_mask, sentinel_mask, spike_mask, stuck_mask, stuck_runs
from .schema import ColumnSpec


@dataclass
class PrepareOptions:
    freq: Optional[str] = None  # regular time step, e.g. "15min" or "1h"; default: the data's typical step
    mask_sentinels: bool = True
    mask_out_of_range: bool = True
    mask_stuck: bool = True
    mask_spikes: bool = True
    stuck_hours: float = 6.0
    fill_limit: Optional[str] = "1h"  # forward-fill input gaps up to this long; None to disable

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _log(log: List[Dict[str, Any]], step: str, detail: str, column: Optional[str] = None, count: Any = None):
    log.append({"step": step, "column": column, "detail": detail, "count": count})


def prepare(df: pd.DataFrame, specs: Mapping[str, ColumnSpec], target: str,
            opts: Optional[PrepareOptions] = None) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    opts = opts or PrepareOptions()
    log: List[Dict[str, Any]] = []
    cols = [c for c in specs if c in df.columns]
    d = df[cols].copy()

    if not d.index.is_monotonic_increasing:
        d = d.sort_index(kind="stable")
        _log(log, "sort", "Sorted rows by time.")

    for c in cols:
        q = specs[c].q
        co = coerce_numeric(d[c], binary=(q.kind == "binary"))
        d[c] = co.values
        n_bad = sum(co.unparseable.values())
        if n_bad:
            _log(log, "text_to_missing", "Text entries that are not numbers set to missing.", c, n_bad)
        if co.n_numbers_in_text:
            _log(log, "text_to_number", "Numbers extracted from text such as '72.5 F'.", c, co.n_numbers_in_text)
        if co.n_words:
            _log(log, "words_to_binary", "Status words (On/Off, ...) read as 1/0.", c, co.n_words)

    if d.index.has_duplicates:
        n_dup = int(d.index.duplicated().sum())
        d = d.groupby(level=0).mean()
        _log(log, "deduplicate", "Averaged rows sharing a timestamp.", None, n_dup)

    step = analyze_index(d.index).step

    for c in cols:
        spec, q = specs[c], specs[c].q
        s = d[c]
        if opts.mask_sentinels:
            m = sentinel_mask(s)
            if m.any():
                s = s.mask(m)
                _log(log, "mask_sentinels", "Placeholder values like -999 set to missing.", c, int(m.sum()))
        if q.canonical_unit is not None and spec.unit in q.units:
            conv = q.units[spec.unit]
            s = pd.Series(conv(s.to_numpy(dtype=float)), index=s.index)
            if spec.unit != q.canonical_unit:
                _log(log, "convert_units", f"Converted {spec.unit} to {q.canonical_unit}.", c)
            if opts.mask_out_of_range:
                m = range_mask(s, q.plausible)
                if m.any():
                    s = s.mask(m)
                    _log(log, "mask_out_of_range", f"Readings outside {q.plausible} {q.canonical_unit} set to missing.",
                         c, int(m.sum()))
        elif q.canonical_unit is not None:
            _log(log, "units_unchecked", f"No valid unit declared; values used as they are ({q.canonical_unit} assumed).", c)
        if opts.mask_stuck and not (q.may_be_constant or spec.flat_ok):
            runs = stuck_runs(s, pd.Timedelta(hours=opts.stuck_hours), ignore_zero=q.zero_runs_ok)
            if runs:
                m = stuck_mask(s, runs, after=pd.Timedelta(hours=opts.stuck_hours))
                s = s.mask(m)
                _log(log, "mask_stuck", f"{len(runs)} stuck stretch(es) set to missing.", c, int(m.sum()))
        if opts.mask_spikes and q.spike_check:
            m = spike_mask(s)
            if m.any():
                s = s.mask(m)
                _log(log, "mask_spikes", "Single-sample spikes set to missing.", c, int(m.sum()))
        d[c] = s

    freq = pd.Timedelta(opts.freq) if opts.freq else step
    if freq is None or freq <= pd.Timedelta(0):
        raise ValueError("Cannot work out a time step from the data; pass freq='15min' (or similar).")
    if step is not None and freq < step:
        _log(log, "warning", f"Requested step {freq} is finer than the data ({step}); many values will be missing.")
    parts = {}
    # A total over an interval is only right if every reading in it is present. Bins with missing
    # readings become missing (never a too-small total), so a missing target is never filled with zeros.
    expected = int(round(freq / step)) if (step is not None and freq >= step) else 1
    for c in cols:
        q = specs[c].q
        r = d[c].resample(freq, label="left", closed="left")
        if q.aggregate == "sum":
            total, count = r.sum(min_count=1), r.count()
            incomplete = count < expected
            if incomplete.any():
                n_bad = int((incomplete & total.notna()).sum())
                total = total.mask(incomplete)
                if n_bad:
                    _log(log, "incomplete_totals", f"Interval totals with missing readings set to missing "
                                                   f"(each needs {expected} readings).", c, n_bad)
            parts[c] = total
        elif q.aggregate == "last":
            parts[c] = r.last()
        else:
            parts[c] = r.mean()
    out = pd.DataFrame(parts)
    out.index.freq = None
    _log(log, "resample", f"Resampled to a regular {fmt_td(freq)} grid ({len(out)} rows).", None, len(out))

    if opts.fill_limit:
        limit = int(pd.Timedelta(opts.fill_limit) / freq)
        if limit >= 1:
            for c in cols:
                if c == target:
                    continue
                before = int(out[c].isna().sum())
                out[c] = out[c].ffill(limit=limit)
                filled = before - int(out[c].isna().sum())
                if filled:
                    _log(log, "forward_fill", f"Filled input gaps up to {opts.fill_limit} with the last known value.",
                         c, filled)
    return out, log


def infer_step(df: pd.DataFrame) -> Optional[pd.Timedelta]:
    return analyze_index(df.index).step
