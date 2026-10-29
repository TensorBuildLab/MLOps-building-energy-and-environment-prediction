"""Data checks: find what is wrong with a building dataset before any model sees it.

Severity levels:
- error:   blocks ``Project.fit()`` until fixed, or accepted with a written reason.
- warning: ``Project.prepare()`` handles it (and logs what it did).
- info:    worth knowing; no action needed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple

import numpy as np
import pandas as pd

from .cleaning import (
    analyze_index,
    coerce_numeric,
    range_mask,
    sentinel_mask,
    spike_mask,
    stuck_runs,
)
from .quantities import guess_unit, to_canonical
from .schema import ColumnSpec


@dataclass
class Issue:
    id: str
    severity: str
    column: Optional[str]
    message: str
    fix: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["evidence"] = {k: str(v) for k, v in self.evidence.items()}
        return d


@dataclass
class DataReport:
    issues: List[Issue]
    summary: Dict[str, Any]

    @property
    def errors(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[Issue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def get(self, issue_id: str) -> Issue:
        for i in self.issues:
            if i.id == issue_id:
                return i
        raise KeyError(issue_id)

    def to_dict(self) -> Dict[str, Any]:
        return {"summary": {k: str(v) for k, v in self.summary.items()},
                "issues": [i.to_dict() for i in self.issues]}

    def to_markdown(self) -> str:
        lines = ["| Severity | Issue | What we found | What happens / what to do |", "|---|---|---|---|"]
        for i in self.issues:
            msg = i.message.replace("|", "\\|")
            fix = i.fix.replace("|", "\\|")
            lines.append(f"| {i.severity} | `{i.id}` | {msg} | {fix} |")
        return "\n".join(lines)

    def __str__(self) -> str:
        s = self.summary
        head = (f"Data check: {s.get('rows')} rows, {s.get('start')} to {s.get('end')}, "
                f"typical step {s.get('step')}. "
                f"{len(self.errors)} error(s), {len(self.warnings)} warning(s).")
        out = [head]
        order = {"error": 0, "warning": 1, "info": 2}
        for i in sorted(self.issues, key=lambda x: order.get(x.severity, 3)):
            out.append(f"[{i.severity.upper()}] {i.id}: {i.message}")
            if i.fix:
                out.append(f"    -> {i.fix}")
        return "\n".join(out)

    __repr__ = __str__


def fmt_td(td: Optional[pd.Timedelta]) -> str:
    if td is None or pd.isna(td):
        return "n/a"
    secs = int(td.total_seconds())
    days, rem = divmod(secs, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days} d")
    if hours:
        parts.append(f"{hours} h")
    if mins:
        parts.append(f"{mins} min")
    if secs and not days:
        parts.append(f"{secs} s")
    return " ".join(parts) or "0 s"


def _examples(values: pd.Series, n: int = 3) -> str:
    vals = values.dropna().unique()[:n]
    return ", ".join(f"{v:g}" if isinstance(v, (int, float, np.floating)) else str(v) for v in vals)


def check_index(df: pd.DataFrame) -> Tuple[List[Issue], Dict[str, Any]]:
    issues: List[Issue] = []
    if not isinstance(df.index, pd.DatetimeIndex):
        issues.append(Issue("index:not_datetime", "error", None,
                            "The data is not indexed by timestamps.",
                            "Parse the timestamp column and set it as the index (or pass timestamp=...)."))
        return issues, {"rows": len(df)}
    info = analyze_index(df.index)
    summary = {"rows": info.n_rows, "start": info.start, "end": info.end, "step": fmt_td(info.step),
               "timezone": info.tz or "none"}
    if info.n_rows < 2 or info.step is None:
        issues.append(Issue("index:too_short", "error", None, "Fewer than two distinct timestamps."))
        return issues, summary
    if not info.is_sorted:
        issues.append(Issue("index:unsorted", "warning", None, "Rows are not in time order.",
                            "prepare() sorts by time."))
    if info.n_duplicates:
        issues.append(Issue(
            "index:duplicates", "warning", None,
            f"{info.n_duplicates} rows repeat a timestamp already present (controller clock resync, "
            f"daylight-saving fall-back, or files merged twice).",
            "prepare() averages rows that share a timestamp.",
            {"n": info.n_duplicates}))
    if info.irregular_fraction > 0.1:
        issues.append(Issue(
            "index:irregular", "warning", None,
            f"{info.irregular_fraction:.0%} of time steps differ from the typical step of {fmt_td(info.step)}. "
            f"Common when a BAS logs on change of value.",
            "prepare() resamples to a regular time grid."))
    if info.gaps:
        longest = max(info.gaps, key=lambda g: g[1] - g[0])
        issues.append(Issue(
            "index:gaps", "warning", None,
            f"{len(info.gaps)} gap(s) longer than 3 time steps, {fmt_td(info.gap_time)} in total; "
            f"longest {fmt_td(longest[1] - longest[0])} from {longest[0]} to {longest[1]}.",
            "Gaps stay missing. Short gaps in inputs are forward-filled; the target is never filled.",
            {"n": len(info.gaps)}))
    if info.tz is None:
        issues.append(Issue(
            "index:no_timezone", "info", None,
            "Timestamps carry no time zone.",
            "Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none)."))
    span = info.end - info.start
    if span < pd.Timedelta(days=14):
        issues.append(Issue(
            "index:short_history", "warning", None,
            f"Only {fmt_td(span)} of data. Weekly patterns cannot be learned and test results will be noisy.",
            "Use more history if you have it."))
    return issues, summary


def check_column(s: pd.Series, spec: ColumnSpec, is_target: bool, stuck_hours: float = 6.0) -> List[Issue]:
    name, q = spec.name, spec.q
    issues: List[Issue] = []
    co = coerce_numeric(s, binary=(q.kind == "binary"))
    v = co.values

    if co.unparseable:
        top = ", ".join(f"'{k}' ({n})" for k, n in co.unparseable.most_common(4))
        issues.append(Issue(f"non_numeric:{name}", "warning", name,
                            f"{sum(co.unparseable.values())} entries are text, not numbers: {top}.",
                            "prepare() treats them as missing.", {"values": dict(co.unparseable)}))
    if co.n_numbers_in_text:
        issues.append(Issue(f"text_numbers:{name}", "info", name,
                            f"{co.n_numbers_in_text} entries had units or separators in the text "
                            f"(like '72.5 F' or '1,234'). The numbers were extracted."))
    if co.n_words:
        issues.append(Issue(f"status_words:{name}", "info", name,
                            f"{co.n_words} status words (On/Off, Occupied/Unoccupied, ...) were read as 1/0."))

    if v.notna().sum() == 0:
        issues.append(Issue(f"empty:{name}", "error", name, "Column has no usable values.",
                            "Remove it from the declarations or fix the export."))
        return issues

    miss = float(v.isna().mean())
    if miss > 0.2:
        severity = "error" if (is_target and miss > 0.5) else "warning"
        issues.append(Issue(f"missing:{name}", severity, name, f"{miss:.0%} of entries are missing.",
                            "Missing target values are skipped, never invented." if is_target
                            else "Models that need complete inputs fill them with the training median."))

    sent = sentinel_mask(v)
    if sent.any():
        issues.append(Issue(f"sentinel:{name}", "warning", name,
                            f"{int(sent.sum())} readings are placeholder values ({_examples(v[sent])}) that "
                            f"controllers write when a reading is missing.",
                            "prepare() treats them as missing.", {"n": int(sent.sum())}))
    v = v.mask(sent)

    unit_ok = q.canonical_unit is None
    if q.canonical_unit is not None:
        if spec.unit is None:
            issues.append(Issue(f"unit_missing:{name}", "error", name,
                                f"No unit declared for {q.name}. Valid units: {', '.join(sorted(q.units))}.",
                                f"Declare it, e.g. '{q.name} [{q.canonical_unit}]'."))
        elif spec.unit not in q.units:
            issues.append(Issue(f"unit_invalid:{name}", "error", name,
                                f"'{spec.unit}' is not a unit of {q.name}. Valid: {', '.join(sorted(q.units))}."))
        else:
            values = v.dropna().to_numpy(dtype=float)
            scores = guess_unit(values, q)
            declared = scores.get(spec.unit, 0.0)
            best = max(scores, key=lambda u: scores[u])
            if declared < 0.5 and best != spec.unit and scores[best] >= 0.9:
                issues.append(Issue(
                    f"unit_mismatch:{name}", "error", name,
                    f"Declared in {spec.unit}, but only {declared:.0%} of values are plausible for {q.name} "
                    f"in {spec.unit}, while {scores[best]:.0%} are plausible in {best} "
                    f"(median value {np.median(values):g}).",
                    f"Check the point's units in the BAS. If they are {best}, declare '{q.name} [{best}]'.",
                    {"scores": scores}))
            elif declared < 0.5:
                issues.append(Issue(
                    f"implausible:{name}", "error", name,
                    f"Only {declared:.0%} of values are plausible for {q.name} in any known unit "
                    f"(median {np.median(values):g}). The declared quantity may be wrong.",
                    "Re-check what this point measures, or declare it as 'other'.", {"scores": scores}))
            else:
                unit_ok = True
    if unit_ok and q.canonical_unit is not None:
        canon = pd.Series(to_canonical(v.to_numpy(dtype=float), q, spec.unit), index=v.index)
        oor = range_mask(canon, q.plausible)
        frac = float(oor.sum() / max(canon.notna().sum(), 1))
        if oor.any():
            lo, hi = q.plausible
            msg = (f"{int(oor.sum())} readings ({frac:.1%}) are outside the plausible range for {q.name} "
                   f"({lo:g} to {hi:g} {q.canonical_unit}), e.g. {_examples(v[oor])} {spec.unit}.")
            if frac > 0.05:
                issues.append(Issue(f"out_of_range:{name}", "error", name, msg,
                                    "That is too many to be sensor glitches: check the declaration.",
                                    {"n": int(oor.sum())}))
            else:
                issues.append(Issue(f"out_of_range:{name}", "warning", name, msg,
                                    "prepare() treats them as missing.", {"n": int(oor.sum())}))
            v = v.mask(oor)

    if not (q.may_be_constant or spec.flat_ok):
        runs = stuck_runs(v, pd.Timedelta(hours=stuck_hours), ignore_zero=q.zero_runs_ok)
        if runs:
            longest = max(runs, key=lambda r: r.duration)
            total = sum((r.duration for r in runs), pd.Timedelta(0))
            msg = (f"Sensor repeats exactly {longest.value:g} for {fmt_td(longest.duration)} "
                   f"({longest.start} to {longest.end}); {len(runs)} such stretch(es), {fmt_td(total)} in total.")
            fix = "prepare() treats these stretches as missing."
            # Change-of-value logging (a new value only when it moves past a deadband) produces long flat
            # stretches that are not faults. Found on real data (Aalborg CO2: 95% of steps unchanged).
            d = v.dropna().diff().dropna()
            unchanged = float((d == 0).mean()) if len(d) else 0.0
            if unchanged > 0.7 and (d != 0).any():
                typical = float(d[d != 0].abs().quantile(0.1))
                msg += (f" The value is unchanged in {unchanged:.0%} of steps and changes by at least ~{typical:g} "
                        f"when it does: this looks like change-of-value logging with a deadband.")
                fix = ("If so, flat stretches are normal: declare the column with flat_ok=True and note why. "
                       "Otherwise prepare() treats them as missing.")
            issues.append(Issue(f"stuck:{name}", "warning", name, msg, fix,
                                {"n_runs": len(runs), "n": int(total.total_seconds() // 60),
                                 "unchanged_share": unchanged}))
        if v.nunique(dropna=True) <= 1:
            issues.append(Issue(f"constant:{name}", "warning", name,
                                "Column never changes, so it carries no information.",
                                "It will be dropped from the model inputs."))

    if q.spike_check:
        spikes = spike_mask(v)
        if spikes.any():
            t0 = v.index[spikes.to_numpy()][0]
            issues.append(Issue(f"spikes:{name}", "warning", name,
                                f"{int(spikes.sum())} single-sample spike(s), e.g. {_examples(v[spikes])} at {t0}.",
                                "prepare() treats them as missing.", {"n": int(spikes.sum())}))

    if q.kind == "interval":
        d = v.dropna().diff().dropna()
        if len(d) > 50 and float((d >= 0).mean()) > 0.95 and v.nunique() > 10:
            issues.append(Issue(
                f"cumulative:{name}", "error", name,
                "Values almost never decrease: this looks like a cumulative meter reading, "
                "not energy per interval.",
                "Take differences first (watch for meter resets), then declare it as energy."))
    return issues


def check_data(df: pd.DataFrame, specs: Mapping[str, ColumnSpec], target: str,
               stuck_hours: float = 6.0) -> DataReport:
    issues, summary = check_index(df)
    summary["target"] = target
    missing = [c for c in specs if c not in df.columns]
    if missing:
        issues.append(Issue("columns:missing", "error", None,
                            f"Declared columns not found in the data: {', '.join(missing)}."))
    undeclared = [c for c in df.columns if c not in specs]
    if undeclared:
        shown = ", ".join(map(str, undeclared[:8])) + (" ..." if len(undeclared) > 8 else "")
        issues.append(Issue("columns:undeclared", "info", None,
                            f"{len(undeclared)} column(s) are not declared and will be ignored: {shown}.",
                            "Declare any you want the model to use."))
    summary["declared_columns"] = len(specs)
    if isinstance(df.index, pd.DatetimeIndex):
        ordered = df.sort_index(kind="stable")
        for name, spec in specs.items():
            if name in ordered.columns:
                issues.extend(check_column(ordered[name], spec, name == target, stuck_hours))
    return DataReport(issues, summary)
