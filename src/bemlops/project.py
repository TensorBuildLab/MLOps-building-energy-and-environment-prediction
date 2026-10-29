"""The main entry point: one prediction task on one building's data.

Typical flow (an AI agent or an engineer can drive it the same way)::

    p = Project(df, target="AHU1_CLG_KW", horizon="1h", columns={...})
    print(p.check_data())     # read the issues
    # fix what needs judgment (your own code), then p.update(...),
    # or p.accept("issue-id", reason="...") if it is fine as it is
    p.prepare(freq="15min")   # standard, logged cleaning
    results = p.fit()         # time-ordered split, baselines, tuned models
    p.save_run("runs/")       # report, model, predictions, full audit record
"""

from __future__ import annotations

import datetime as _dt
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

import numpy as np
import pandas as pd
from sklearn.base import clone

from ._version import __version__
from .checks import DataReport, check_data, fmt_td
from .deploy import ForecastModel
from .features import audit, build_features, steps_in, suspicious_inputs, target_shifts
from .metrics import guideline14, regression_metrics, skill_score
from .models import Persistence, TrainMean, candidates, tune
from .prepare import PrepareOptions, prepare
from .schema import ColumnSpec, parse_columns
from .split import time_split


class UnresolvedIssues(RuntimeError):
    """fit() was called while the data check still has errors nobody has dealt with."""


@dataclass
class Results:
    task: Dict[str, Any]
    split: Dict[str, Any]
    validation: pd.DataFrame
    chosen: str
    chosen_params: Dict[str, Any]
    test: Dict[str, float]
    baseline_name: str
    test_baseline: Dict[str, float]
    skill: float
    guideline14: Optional[Dict[str, Any]]
    predictions: pd.DataFrame
    features: List[Dict[str, Any]]
    model: ForecastModel
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        t, u = self.task, self.task.get("unit") or ""
        lines = [f"Task: {t['description']}",
                 f"Rows used: train {self.split['sizes']['train']}, validation {self.split['sizes']['val']}, "
                 f"test {self.split['sizes']['test']} (time-ordered, gap {self.split['gap']}).",
                 "Validation results (lower RMSE is better):"]
        cols = [c for c in ["model", "rmse", "mae", "cvrmse_pct", "nmbe_pct", "r2"] if c in self.validation]
        lines.append(self.validation[cols].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
        m = self.test
        line = f"Chosen: {self.chosen}. Test: RMSE {m['rmse']:.3g} {u}, MAE {m['mae']:.3g} {u}"
        if "cvrmse_pct" in m:
            line += f", CV(RMSE) {m['cvrmse_pct']:.1f}%, NMBE {m['nmbe_pct']:.1f}%"
        lines.append(line + ".")
        lines.append(f"Skill vs {self.baseline_name}: {self.skill:.2f} (1 = perfect, 0 = no better than the baseline).")
        if self.guideline14:
            g = self.guideline14
            verdict = "passes" if g["passes"] else "does not pass"
            lines.append(f"ASHRAE Guideline 14 ({g['resolution']}): CV(RMSE) {g['cvrmse_pct']:.1f}% "
                         f"(limit {g['cvrmse_limit']:.0f}%), NMBE {g['nmbe_pct']:.1f}% "
                         f"(limit +/-{g['nmbe_limit']:.0f}%): {verdict}.")
        for w in self.warnings:
            lines.append(f"Warning: {w}")
        return "\n".join(lines)

    __str__ = summary
    __repr__ = summary


class Project:
    def __init__(self, data: pd.DataFrame, target: str,
                 columns: Mapping[str, Union[str, Mapping[str, Any], ColumnSpec]],
                 horizon: Union[int, str, pd.Timedelta] = 0, timestamp: Optional[str] = None,
                 timestamp_format: Optional[str] = None, name: Optional[str] = None):
        """
        data:      the building data, indexed by time (or pass `timestamp` = the time column).
        target:    the column to predict.
        columns:   what every column you want to use means, e.g.
                   {"RM204_ZN_T": "zone_air_temperature [degF]", "OAT": "outdoor_air_temperature [degF]"}.
                   Undeclared columns are ignored.
        horizon:   how far ahead to predict, e.g. "1h" or 4 (steps). 0 means estimate the
                   target from inputs measured at the same moment (virtual sensor).
        timestamp_format: e.g. "%m/%d/%Y %I:%M:%S %p". Recommended: avoids day/month mix-ups.
        """
        self.name = name or f"{target}"
        self.log: List[Dict[str, Any]] = []
        df = data.copy()
        if timestamp is not None:
            if timestamp_format:
                ts = pd.to_datetime(df[timestamp], format=timestamp_format, errors="coerce")
            else:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    ts = pd.to_datetime(df[timestamp], errors="coerce")
                self._event("timestamps", "Timestamp format was guessed; pass timestamp_format to be sure.")
            bad = int(ts.isna().sum())
            df = df.drop(columns=[timestamp])
            df.index = pd.DatetimeIndex(ts)
            if bad:
                df = df[df.index.notna()]
                self._event("timestamps", f"{bad} rows had unreadable timestamps and were dropped.")
        elif not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index)
            except (ValueError, TypeError) as exc:
                raise ValueError("The data needs a time index. Pass timestamp='<time column>' "
                                 "or set a DatetimeIndex first.") from exc
        self.raw = df
        self.specs: Dict[str, ColumnSpec] = parse_columns(columns)
        if target not in self.specs:
            raise ValueError(f"Declare the target too, e.g. columns={{'{target}': '<quantity> [<unit>]', ...}}.")
        self.target = target
        self.horizon = horizon
        self.accepted: Dict[str, str] = {}
        self.notes: List[str] = []
        self.report_: Optional[DataReport] = None
        self.data: Optional[pd.DataFrame] = None
        self.prepare_log: List[Dict[str, Any]] = []
        self.prepare_options: Optional[PrepareOptions] = None
        self.results: Optional[Results] = None

    # ----- bookkeeping -------------------------------------------------
    def _event(self, kind: str, detail: str) -> None:
        self.log.append({"time": _dt.datetime.now().isoformat(timespec="seconds"), "kind": kind, "detail": detail})

    def note(self, text: str) -> None:
        """Record a decision and why (e.g. 'Dropped AHU2: disconnected during retrofit'). Goes into the run record."""
        self.notes.append(text)
        self._event("note", text)

    def accept(self, issue_id: str, reason: str) -> None:
        """Accept a reported error as it is. A written reason is required and kept in the run record."""
        if not reason or len(reason.strip()) < 10:
            raise ValueError("Give a real reason (at least a short sentence) for accepting an issue.")
        if self.report_ is not None:
            self.report_.get(issue_id)  # raises KeyError for an unknown id
        self.accepted[issue_id] = reason.strip()
        self._event("accept", f"{issue_id}: {reason.strip()}")

    def update(self, data: Optional[pd.DataFrame] = None,
               columns: Optional[Mapping[str, Any]] = None, drop: Sequence[str] = (),
               note: Optional[str] = None) -> None:
        """Swap in fixed data, corrected or new declarations, or drop columns. Checks run again before fitting."""
        if data is not None:
            if not isinstance(data.index, pd.DatetimeIndex):
                raise ValueError("Updated data needs a DatetimeIndex.")
            self.raw = data.copy()
        if columns is not None:
            new = parse_columns(columns)
            self.specs.update(new)
        for c in drop:
            if c == self.target:
                raise ValueError("The target cannot be dropped.")
            self.specs.pop(c, None)
        if self.target not in self.specs:
            raise ValueError("The target must stay declared.")
        self.report_, self.data, self.results = None, None, None
        self._event("update", note or "Data or declarations updated.")
        if note:
            self.notes.append(note)

    # ----- the workflow --------------------------------------------------
    @property
    def mode(self) -> str:
        return "estimate" if self._horizon_is_zero() else "forecast"

    def _horizon_is_zero(self) -> bool:
        h = self.horizon
        return (isinstance(h, (int, np.integer)) and h == 0) or (not isinstance(h, (int, np.integer))
                                                                  and pd.Timedelta(h) == pd.Timedelta(0))

    def check_data(self, stuck_hours: float = 6.0) -> DataReport:
        self.report_ = check_data(self.raw, self.specs, self.target, stuck_hours=stuck_hours)
        self._event("check", f"{len(self.report_.errors)} errors, {len(self.report_.warnings)} warnings")
        return self.report_

    def prepare(self, freq: Optional[str] = None, **options: Any) -> pd.DataFrame:
        """Standard cleaning (see bemlops.prepare). Options: mask_stuck, mask_spikes, fill_limit, ..."""
        self.prepare_options = PrepareOptions(freq=freq, **options)
        self.data, self.prepare_log = prepare(self.raw, self.specs, self.target, self.prepare_options)
        self._event("prepare", f"{len(self.data)} rows on a {self.step} grid")
        return self.data

    @property
    def step(self) -> pd.Timedelta:
        if self.data is None:
            raise RuntimeError("Run prepare() first.")
        return pd.Timedelta(self.data.index[1] - self.data.index[0])

    @property
    def horizon_steps(self) -> int:
        h = self.horizon
        if isinstance(h, (int, np.integer)):
            return int(h)
        ratio = pd.Timedelta(h) / self.step
        if abs(ratio - round(ratio)) > 1e-9:
            raise ValueError(f"Horizon {h} is not a whole number of {self.step} steps.")
        return int(round(ratio))

    def _blocking(self) -> List[Any]:
        return [i for i in self.report_.errors if i.id not in self.accepted]

    def fit(self, models: Sequence[str] = ("ridge", "random_forest", "gbm"), n_iter: int = 10,
            fractions=(0.7, 0.15, 0.15), random_state: int = 0) -> Results:
        if self.report_ is None:
            self.check_data()
        blocking = self._blocking()
        if blocking:
            lines = ["The data check found errors that need a decision before fitting:"]
            for i in blocking:
                lines.append(f"  - {i.id}: {i.message}" + (f" ({i.fix})" if i.fix else ""))
            lines.append("Fix the data or declarations and call update(...), "
                         "or accept an issue with accept(id, reason='...').")
            raise UnresolvedIssues("\n".join(lines))
        if self.data is None:
            self.prepare()

        data, step, h, target = self.data, self.step, self.horizon_steps, self.target
        lags = target_shifts(h, step, len(data)) if h > 0 else []
        X, y, feats = build_features(data, target, self.specs, h, step, target_lags=lags)
        audit(feats, target, h)
        warnings_ = suspicious_inputs(X, y, feats, target)

        usable = y.notna().to_numpy()
        Xu, yu = X[usable], y[usable]
        if len(yu) < 200:
            raise ValueError(f"Only {len(yu)} rows have a target value; at least 200 are needed.")
        gap = h * step
        sp = time_split(Xu.index, fractions, gap=gap)
        Xtr, ytr, Xva, yva, Xte, yte = Xu[sp.train], yu[sp.train], Xu[sp.val], yu[sp.val], Xu[sp.test], yu[sp.test]

        if h > 0:
            baselines = {"persistence": Persistence(f"{target}__t-{h}")}
            day = steps_in("1D", step)
            if f"{target}__t-{day}" in X.columns:
                baselines["same_time_yesterday"] = Persistence(f"{target}__t-{day}")
            ref_name = "persistence"
        else:
            baselines = {"training_mean": TrainMean()}
            ref_name = "training_mean"

        rows, fitted = [], {}
        for name, est in baselines.items():
            est.fit(Xtr, ytr)
            rows.append({"model": name, "type": "baseline", **regression_metrics(yva, est.predict(Xva)),
                         "params": {}})
            fitted[name] = (est, {})
        pool = candidates(random_state)
        for name in models:
            if name not in pool:
                raise ValueError(f"Unknown model '{name}'. Available: {sorted(pool)}")
            est, space = pool[name]
            best, params, cv_rmse = tune(est, space, Xtr, ytr, gap_steps=h, n_iter=n_iter, random_state=random_state)
            rows.append({"model": name, "type": "ml", **regression_metrics(yva, best.predict(Xva)),
                         "cv_rmse": cv_rmse, "params": params})
            fitted[name] = (est, params)
        validation = pd.DataFrame(rows).sort_values("rmse").reset_index(drop=True)
        chosen = str(validation.iloc[0]["model"])
        base_est, params = fitted[chosen]

        trval = sp.train | sp.val
        final = clone(base_est).set_params(**params) if params else clone(base_est)
        final.fit(Xu[trval], yu[trval])
        pred = final.predict(Xte)
        ref = clone(baselines[ref_name]).fit(Xu[trval], yu[trval])
        ref_pred = ref.predict(Xte)
        test_m = regression_metrics(yte, pred)
        ref_m = regression_metrics(yte, ref_pred)
        skill = skill_score(test_m["rmse"], ref_m["rmse"])

        spec = self.specs[target]
        q = spec.q
        g14 = None
        predictions = pd.DataFrame({"actual": yte, "predicted": pred, ref_name: ref_pred}, index=Xte.index)
        if q.headline_metric == "cvrmse" and step <= pd.Timedelta("1h"):
            # Guideline 14's hourly criteria, applied to hourly totals or means.
            g14 = guideline14(predictions["actual"], predictions["predicted"], aggregate=q.aggregate)
        if chosen in baselines:
            warnings_.append(f"No machine-learning model beat the '{chosen}' baseline on validation data. "
                             f"Look for better inputs before deploying anything more complex.")
        elif skill < 0.05:
            warnings_.append(f"The model is barely better than {ref_name} on test data (skill {skill:.2f}).")

        train_rows = data.loc[: sp.bounds["val"][1]]
        ranges = {}
        for c in self.specs:
            if c != target and c in train_rows.columns and train_rows[c].notna().any():
                lo, hi = np.nanpercentile(train_rows[c], [1, 99])
                ranges[c] = (float(lo), float(hi))
        unit = q.canonical_unit
        horizon_text = (f"{fmt_td(h * step)} ahead ({h} step(s) of {fmt_td(step)})" if h > 0
                        else "at the same moment as its inputs (estimation / virtual sensor)")
        task = {"target": target, "quantity": q.name, "unit": unit, "mode": self.mode, "horizon_steps": h,
                "step": str(step), "description": f"{self.mode} {target} ({q.name}, {unit}) {horizon_text}"}
        model = ForecastModel(
            target=target, specs=dict(self.specs), horizon=h, step=step,
            prepare_options=self.prepare_options, estimator=final, model_name=chosen,
            feature_names=list(X.columns), target_lags=lags, include_doy="doy_sin" in X.columns,
            input_ranges=ranges, test_rmse=test_m["rmse"], train_end=sp.bounds["val"][1],
            version=__version__, trained_at=_dt.datetime.now().isoformat(timespec="seconds"), unit=unit)
        self.results = Results(
            task=task,
            split={"sizes": sp.sizes(), "gap": fmt_td(gap),
                   "bounds": {k: (str(a), str(b)) for k, (a, b) in sp.bounds.items()}},
            validation=validation, chosen=chosen, chosen_params=params, test=test_m,
            baseline_name=ref_name, test_baseline=ref_m, skill=skill, guideline14=g14,
            predictions=predictions, features=[f.to_dict() for f in feats], model=model, warnings=warnings_)
        self._event("fit", f"chosen {chosen}, test RMSE {test_m['rmse']:.4g}")
        return self.results

    def save_run(self, out_dir: Union[str, Path] = "runs") -> Path:
        """Write the report, model, test predictions and the full audit record to a new folder."""
        from .report import write_run

        return write_run(self, Path(out_dir))
