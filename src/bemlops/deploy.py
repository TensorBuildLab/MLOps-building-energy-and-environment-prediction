"""The trained model as a deployable object: forecast on new data, watch for drift, save and load.

The same preparation and feature steps used in training are replayed on new
data, so a model in operation sees its inputs exactly as it did in training.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd

from .features import build_features
from .metrics import regression_metrics
from .prepare import PrepareOptions, prepare
from .schema import ColumnSpec


@dataclass
class DriftReport:
    rmse_now: float
    rmse_at_test: float
    ratio: float
    inputs_out_of_range: Dict[str, float]
    retrain_recommended: bool
    message: str

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
    test_rmse: float
    train_end: pd.Timestamp
    version: str
    trained_at: str
    unit: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def _prepare(self, data: pd.DataFrame) -> pd.DataFrame:
        opts = replace(self.prepare_options, freq=str(self.step))
        prepared, _ = prepare(data, self.specs, self.target, opts)
        return prepared

    def _predict_prepared(self, prepared: pd.DataFrame) -> pd.DataFrame:
        X, y, _ = build_features(prepared, self.target, self.specs, self.horizon, self.step,
                                 target_lags=self.target_lags, include_doy=self.include_doy)
        X = X.reindex(columns=self.feature_names)
        out = pd.DataFrame({"predicted": self.estimator.predict(X), "actual": y}, index=X.index)
        out["forecast_made_at"] = out.index - self.horizon * self.step
        return out

    def predict(self, data: pd.DataFrame, future: bool = True) -> pd.DataFrame:
        """Predictions for every time step in `data`.

        With future=True (forecast mode) the result also covers the next
        `horizon` steps after the data ends: those rows are the live forecast.
        Raw data is fine; it goes through the same preparation as in training.
        """
        prepared = self._prepare(data)
        if future and self.horizon > 0:
            ahead = pd.date_range(prepared.index[-1] + self.step, periods=self.horizon, freq=self.step)
            prepared = prepared.reindex(prepared.index.append(ahead))
        return self._predict_prepared(prepared)

    def check_drift(self, recent: pd.DataFrame, tolerance: float = 1.5,
                    max_out_of_range: float = 0.2) -> DriftReport:
        """Compare accuracy on recent data with accuracy at test time, and inputs with training data."""
        prepared = self._prepare(recent)
        out = self._predict_prepared(prepared)
        # Skip the warm-up rows whose lag inputs reach back before the window starts.
        warmup = max(self.target_lags + [self.horizon + int(pd.Timedelta("1D") / self.step)]) if self.horizon else 0
        out = out.iloc[warmup:]
        if out["actual"].notna().sum() < 10:
            raise ValueError("Not enough recent data with known targets to judge drift; pass a longer window.")
        m = regression_metrics(out["actual"], out["predicted"])
        rmse = m.get("rmse", float("nan"))
        ratio = rmse / self.test_rmse if self.test_rmse else float("nan")
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
        shifted = {c: s for c, s in oor.items() if s > max_out_of_range}
        parts = [f"Recent RMSE {rmse:.3g} vs {self.test_rmse:.3g} at test time ({ratio:.2f}x)."]
        if degraded:
            parts.append("Accuracy has degraded beyond the tolerance.")
        if shifted:
            parts.append("Inputs outside the training range: " +
                         ", ".join(f"{c} ({s:.0%})" for c, s in shifted.items()) + ".")
        retrain = degraded or bool(shifted)
        parts.append("Retraining on recent data is recommended." if retrain else "No action needed.")
        return DriftReport(rmse, self.test_rmse, ratio, oor, retrain, " ".join(parts))

    def save(self, path: Union[str, Path]) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        return path


def load_model(path: Union[str, Path]) -> ForecastModel:
    model = joblib.load(path)
    if not isinstance(model, ForecastModel):
        raise TypeError(f"{path} does not contain a bemlops ForecastModel.")
    return model
