"""The trained model as a deployable object: predict on new data, validate it, watch for drift.

The same timestamp parsing, data checks, preparation and feature steps used in
training are replayed on new data, so a model in operation sees its inputs
exactly as it did in training, and bad live data is caught before it is used.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd

from .checks import DataReport, Issue, check_data
from .features import build_features
from .metrics import PRIMARY_METRIC, evaluate
from .models import scores
from .prepare import PrepareOptions, prepare
from .schema import ColumnSpec, to_time_index


class InvalidInputData(RuntimeError):
    """Live data failed the checks the model was trained under."""


@dataclass
class DriftReport:
    metric: str
    error_now: float
    error_at_test: float
    ratio: float
    inputs_out_of_range: Dict[str, float]
    data_issues: List[str]
    retrain_recommended: bool
    message: str
    baseline_error: Optional[float] = None  # persistence on the same recent rows (forecasts)
    worse_than_baseline: bool = False

    def __str__(self) -> str:
        return self.message


@dataclass
class ForecastModel:
    target: str
    specs: Dict[str, ColumnSpec]
    horizon: int
    step: pd.Timedelta
    prepare_options: PrepareOptions
    estimator: Any
    model_name: str
    feature_names: List[str]
    target_lags: List[int]
    include_doy: bool
    input_ranges: Dict[str, Tuple[float, float]]
    test_error: float
    train_end: pd.Timestamp
    version: str
    trained_at: str
    unit: Optional[str] = None
    task: str = "regression"
    timestamp: Optional[str] = None
    timestamp_format: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    train_start: Optional[pd.Timestamp] = None
    target_range: Optional[Tuple[float, float]] = None
    holidays: List[str] = field(default_factory=list)
    interval_half_width: Optional[float] = None  # nominal 90% interval, calibrated on validation errors
    tz: Optional[str] = None  # time zone given at training (tz=...)
    index_tz: Optional[str] = None  # time zone of the training index (None = naive)
    last_check_: Optional[DataReport] = None

    # ----- input handling ----------------------------------------------------
    def _index(self, data: pd.DataFrame) -> pd.DataFrame:
        has_ts = self.timestamp is not None and self.timestamp in data.columns
        df, _ = to_time_index(data, self.timestamp if has_ts else None, self.timestamp_format, tz=self.tz)
        live_tz = None if df.index.tz is None else str(df.index.tz)
        if self.index_tz and live_tz is None:
            raise InvalidInputData(f"Live data has no time zone, but the model was trained in {self.index_tz}.")
        if not self.index_tz and live_tz is not None:
            raise InvalidInputData(f"Live data is in {live_tz}, but the model was trained on local times without "
                                   f"a zone. Convert to the same local time and drop the zone.")
        if self.index_tz and live_tz != self.index_tz:
            df.index = df.index.tz_convert(self.index_tz)
        if self.target not in df.columns:
            if self.horizon > 0:
                raise InvalidInputData(f"Forecasting needs recent values of the target '{self.target}'.")
            df[self.target] = np.nan  # a virtual sensor runs without the target
        return df

    def _skew_issues(self, prepared: pd.DataFrame) -> List[Issue]:
        """Training-serving skew: live inputs far outside what the model saw in training.

        Catches what range checks cannot, e.g. an outdoor temperature feed that switched
        from degF to degC: both are plausible outdoor values, but not for this building's history.
        """
        issues = []
        for c, (lo, hi) in self.input_ranges.items():
            if c not in prepared.columns:
                continue
            v = prepared[c].dropna()
            if len(v) < 20:
                continue
            margin = 0.1 * (hi - lo) if hi > lo else 0.1 * abs(hi) + 1e-9
            share = float(((v < lo - margin) | (v > hi + margin)).mean())
            if share > 0.2:
                unit = self.specs[c].q.canonical_unit or ""
                issues.append(Issue(
                    f"input_shift:{c}", "error" if share > 0.8 else "warning", c,
                    f"{share:.0%} of live values are outside the range seen in training ({lo:.3g} to {hi:.3g} "
                    f"{unit}); the live median is {v.median():.3g}. A changed unit, a broken sensor, or "
                    f"conditions the model has never seen.",
                    "Check the feed first. If the building really is operating outside its history, retrain."))
        return issues

    def _validate(self, data: pd.DataFrame, on_error: str) -> Tuple[DataReport, pd.DataFrame]:
        df = self._index(data)
        specs = dict(self.specs)
        if self.horizon == 0:
            specs.pop(self.target)  # not measured in operation
        missing = [c for c in specs if c not in df.columns]
        report = check_data(df, specs, self.target)
        prepared = self._prepare(df)
        report.issues.extend(self._skew_issues(prepared))
        self.last_check_ = report
        if (missing or report.errors) and on_error == "raise":
            problems = [f"missing columns: {missing}"] if missing else []
            problems += [f"{i.id}: {i.message}" for i in report.errors]
            raise InvalidInputData("Live data failed the checks:\n  - " + "\n  - ".join(problems) +
                                   "\nFix the feed, or call predict(..., on_error='warn') to proceed anyway.")
        return report, prepared

    def validate(self, data: pd.DataFrame, on_error: str = "raise") -> DataReport:
        """Run the training-time data checks, plus a training-vs-live comparison, on live data."""
        return self._validate(data, on_error)[0]

    def _prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        opts = replace(self.prepare_options, freq=str(self.step))
        prepared, _ = prepare(df, self.specs, self.target, opts)
        return prepared

    def _predict_prepared(self, prepared: pd.DataFrame) -> pd.DataFrame:
        X, y, _ = build_features(prepared, self.target, self.specs, self.horizon, self.step,
                                 target_lags=self.target_lags, include_doy=self.include_doy,
                                 holidays=self.holidays, drop_constant=False)
        X = X.reindex(columns=self.feature_names)
        missing_inputs = X.isna().sum(axis=1).astype(int)
        s = scores(self.estimator, X, self.task)
        if self.task == "classification":
            actual = y.where(y.isna(), (y >= 0.5).astype(float))
            out = pd.DataFrame({"probability": s, "predicted": (s >= 0.5).astype(int), "actual": actual},
                               index=X.index)
        else:
            out = pd.DataFrame({"predicted": s, "actual": y}, index=X.index)
            if self.interval_half_width is not None:
                lo_b, hi_b = self.specs[self.target].q.plausible
                out["lower"] = np.minimum(np.maximum(s - self.interval_half_width, lo_b), s)
                out["upper"] = np.maximum(np.minimum(s + self.interval_half_width, hi_b), s)
        # Bins are labelled by their start, so the last input bin (T - h) is complete at T - (h - 1) steps.
        out["forecast_available_at"] = out.index - (self.horizon - 1) * self.step
        out["inputs_missing"] = missing_inputs  # > 0: warm-up rows or gaps; those inputs were imputed
        return out

    # ----- public API ----------------------------------------------------------
    def predict(self, data: pd.DataFrame, future: bool = True, validate: bool = True,
                on_error: str = "raise", future_inputs: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Predictions for every time step in `data` (raw data is fine).

        validate:  check the live data first, as in training (results in `last_check_`).
        on_error:  "raise" (default) stops on failed checks; "warn" goes ahead.
        future:    in forecast mode, also cover the next `horizon` steps after the data
                   ends; those rows are the live forecast.
        future_inputs: values of known-ahead inputs (weather forecasts, schedules) for those future
                   rows, in the same format as `data`. Without them, known-ahead inputs are imputed
                   there, and `inputs_missing` says so.
        Pass at least a week of history so that every lag input exists for the live rows.
        """
        if validate:
            _, prepared = self._validate(data, on_error)
        else:
            prepared = self._prepare(self._index(data))
        if future and self.horizon > 0:
            ahead = pd.date_range(prepared.index[-1] + self.step, periods=self.horizon, freq=self.step)
            prepared = prepared.reindex(prepared.index.append(ahead))
        if future_inputs is not None:
            known = [c for c, s in self.specs.items() if s.known_ahead]
            fi = self._prepare(self._index(future_inputs))
            for c in known:
                if c in fi.columns:
                    prepared[c] = prepared[c].combine_first(fi[c].reindex(prepared.index))
        return self._predict_prepared(prepared)

    def check_drift(self, recent: pd.DataFrame, tolerance: float = 1.5,
                    max_out_of_range: float = 0.2) -> DriftReport:
        """Is the model still fit for use? Checks accuracy, input ranges and live data quality."""
        report, prepared = self._validate(recent, on_error="warn")
        out = self._predict_prepared(prepared)
        # Skip the warm-up rows whose lag inputs reach back before the window starts.
        warmup = max(self.target_lags + [self.horizon + int(pd.Timedelta("1D") / self.step)]) if self.horizon else 0
        out = out.iloc[warmup:]
        if out["actual"].notna().sum() < 10:
            raise ValueError("Not enough recent data with known targets to judge drift; pass a longer window.")
        metric = PRIMARY_METRIC[self.task]
        s = out["probability"] if self.task == "classification" else out["predicted"]
        err = evaluate(out["actual"], s, self.task).get(metric, float("nan"))
        ratio = err / self.test_error if self.test_error else float("nan")
        oor: Dict[str, float] = {}
        for c, (lo, hi) in self.input_ranges.items():
            if c in prepared.columns:
                v = prepared[c].dropna()
                if len(v):
                    margin = 0.1 * (hi - lo) if hi > lo else 0.0
                    share = float(((v < lo - margin) | (v > hi + margin)).mean())
                    if share > 0:
                        oor[c] = share
        degraded = bool(np.isfinite(ratio) and ratio > tolerance)
        # Compare with "same as before" on the same rows: a model can stay close to its own test-time
        # error and still lose to persistence (found on district heating in summer, heating off).
        base_err, worse = None, False
        if self.horizon > 0:
            persist = out["actual"].shift(self.horizon)
            if self.task == "classification":
                persist = persist.clip(0, 1)
            both = pd.concat({"a": out["actual"], "p": persist}, axis=1).dropna()
            if len(both) >= 10:
                base_err = evaluate(both["a"], both["p"], self.task).get(metric)
                worse = bool(base_err is not None and np.isfinite(base_err) and err > base_err)
        shifted = {c: s_ for c, s_ in oor.items() if s_ > max_out_of_range}
        new_faults = [i.id for i in report.issues if i.severity in ("error", "warning")
                      and i.id.split(":")[0] in ("stuck", "unit_mismatch", "implausible", "out_of_range",
                                                 "empty", "missing", "sentinel", "spikes")]
        parts = [f"Recent {metric} {err:.3g} vs {self.test_error:.3g} at test time ({ratio:.2f}x)."]
        if degraded:
            parts.append("Accuracy has degraded beyond the tolerance.")
        if shifted:
            parts.append("Inputs outside the training range: " +
                         ", ".join(f"{c} ({s_:.0%})" for c, s_ in shifted.items()) + ".")
        if new_faults:
            parts.append("Data-quality issues in the live feed: " + ", ".join(new_faults) + ".")
        if worse:
            parts.append(f"The model is worse than persistence on these rows ({err:.3g} vs {base_err:.3g}): "
                         f"fall back to persistence until a retrained model beats it.")
        retrain = degraded or bool(shifted) or worse
        if retrain:
            parts.append("Retraining on recent data is recommended.")
        elif new_faults:
            parts.append("Fix the sensor or feed issues; retraining will not help with those.")
        else:
            parts.append("No action needed.")
        return DriftReport(metric, err, self.test_error, ratio, oor, new_faults, retrain, " ".join(parts),
                           base_err, worse)

    def save(self, path: Union[str, Path]) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.last_check_ = None
        # Parallel tree prediction sums in a varying order (differences ~1e-15); one thread repeats exactly.
        try:
            params = self.estimator.get_params(deep=True)
            self.estimator.set_params(**{k: 1 for k in params if k == "n_jobs" or k.endswith("__n_jobs")})
        except (AttributeError, ValueError):
            pass
        joblib.dump(self, path)
        return path


def load_model(path: Union[str, Path]) -> ForecastModel:
    model = joblib.load(path)
    if not isinstance(model, ForecastModel):
        raise TypeError(f"{path} does not contain a bemlops ForecastModel.")
    return model
