"""Model candidates and simple baselines, for numeric and yes/no targets.

Every run is compared against a baseline that needs no machine learning:
persistence (the latest known value) for forecasts, the training mean (or
the share of "yes") for estimates. A model that cannot beat that is not
worth deploying, and the report says so.
"""

from __future__ import annotations

import warnings
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import loguniform
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin, clone
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# ----- baselines --------------------------------------------------------------
class Persistence(BaseEstimator, RegressorMixin):
    """Predict the value of one input column, e.g. the latest known target value."""

    def __init__(self, column: str = ""):
        self.column = column

    def fit(self, X: pd.DataFrame, y=None):
        self.fallback_ = float(np.nanmean(np.asarray(y, dtype=float))) if y is not None else 0.0
        return self

    def predict(self, X: pd.DataFrame):
        v = X[self.column].to_numpy(dtype=float)
        return np.where(np.isfinite(v), v, self.fallback_)


class TrainMean(BaseEstimator, RegressorMixin):
    def fit(self, X, y):
        self.mean_ = float(np.nanmean(np.asarray(y, dtype=float)))
        return self

    def predict(self, X):
        return np.full(len(X), self.mean_)


class ProfileBaseline(BaseEstimator, RegressorMixin):
    """Mean of the target by time of day, separately for weekdays and weekends (training data only).
    The fair no-ML reference for scheduled loads, where "same as an hour ago" is weak."""

    @staticmethod
    def _keys(idx: pd.DatetimeIndex) -> pd.MultiIndex:
        return pd.MultiIndex.from_arrays([(idx.day_of_week >= 5).astype(int), idx.hour, idx.minute])

    def fit(self, X: pd.DataFrame, y):
        yy = pd.Series(np.asarray(y, dtype=float), index=self._keys(X.index))
        self.table_ = yy.groupby(level=[0, 1, 2]).mean()
        self.mean_ = float(np.nanmean(yy))
        return self

    def predict(self, X: pd.DataFrame):
        return self.table_.reindex(self._keys(X.index)).fillna(self.mean_).to_numpy(dtype=float)


class TimeOfWeekProfile(BaseEstimator, RegressorMixin):
    """Mean of the target for each time of week (day of week x time of day), training data only.

    Stronger than the weekday/weekend profile for buildings whose schedule differs between weekdays.
    Times of week never seen in training fall back to the weekday/weekend profile."""

    @staticmethod
    def _keys(idx: pd.DatetimeIndex) -> pd.MultiIndex:
        return pd.MultiIndex.from_arrays([idx.day_of_week, idx.hour, idx.minute])

    def fit(self, X: pd.DataFrame, y):
        yy = pd.Series(np.asarray(y, dtype=float), index=self._keys(X.index))
        self.table_ = yy.groupby(level=[0, 1, 2]).mean()
        self.fallback_ = ProfileBaseline().fit(X, y)
        return self

    def predict(self, X: pd.DataFrame):
        p = self.table_.reindex(self._keys(X.index)).to_numpy(dtype=float)
        return np.where(np.isfinite(p), p, self.fallback_.predict(X))


class TOWTBaseline(BaseEstimator, RegressorMixin):
    """Time-of-week-and-temperature regression (Mathieu et al. 2011), fitted by least squares.

    One level per time of week plus a piecewise-linear term in outdoor temperature with fixed knots at
    30, 45, 55, 65, 75 and 90 degF (the CalTRACK hourly knots), without occupancy splitting. It is the
    standard no-machine-learning reference in measurement and verification. `temperature` names the
    temperature input available at prediction time: the measured value for estimates, the value lagged
    by the horizon for forecasts (no weather forecast is assumed)."""

    KNOTS_C = (-1.111, 7.222, 12.778, 18.333, 23.889, 32.222)

    def __init__(self, temperature: str = "", ridge: float = 1e-6):
        self.temperature = temperature
        self.ridge = ridge

    def _temp_basis(self, t: np.ndarray) -> np.ndarray:
        k = self.KNOTS_C
        cols = [np.minimum(t, k[0])]
        for a, b in zip(k[:-1], k[1:]):
            cols.append(np.clip(t, a, b) - a)
        cols.append(np.maximum(t, k[-1]) - k[-1])
        return np.column_stack(cols)

    def _design(self, X: pd.DataFrame) -> np.ndarray:
        keys = self._tow_keys(X.index)
        onehot = np.zeros((len(X), len(self.levels_)))
        pos = pd.Index(self.levels_).get_indexer(keys)
        seen = pos >= 0
        onehot[np.flatnonzero(seen), pos[seen]] = 1.0
        t = X[self.temperature].to_numpy(dtype=float)
        t = np.where(np.isfinite(t), t, self.t_mean_)
        return np.column_stack([onehot, self._temp_basis(t)]), seen

    @staticmethod
    def _tow_keys(idx: pd.DatetimeIndex) -> np.ndarray:
        return (idx.day_of_week * 1440 + idx.hour * 60 + idx.minute).to_numpy()

    def fit(self, X: pd.DataFrame, y):
        yy = np.asarray(y, dtype=float)
        self.levels_ = np.unique(self._tow_keys(X.index))
        t = X[self.temperature].to_numpy(dtype=float)
        self.t_mean_ = float(np.nanmean(t)) if np.isfinite(t).any() else 0.0
        A, _ = self._design(X)
        ok = np.isfinite(yy)
        A, yy = A[ok], yy[ok]
        self.coef_ = np.linalg.solve(A.T @ A + self.ridge * np.eye(A.shape[1]), A.T @ yy)
        self.fallback_ = TimeOfWeekProfile().fit(X, y)
        return self

    def predict(self, X: pd.DataFrame):
        A, seen = self._design(X)
        return np.where(seen, A @ self.coef_, self.fallback_.predict(X))


class ProbabilityProfile(BaseEstimator, ClassifierMixin):
    """Probability of 'yes' = its share at that time of day in training, weekdays and weekends apart."""

    def fit(self, X: pd.DataFrame, y):
        self.classes_ = np.array([0, 1])
        self.profile_ = ProfileBaseline().fit(X, np.asarray(y, dtype=float))
        return self

    def predict_proba(self, X: pd.DataFrame):
        p = np.clip(self.profile_.predict(X), 0.0, 1.0)
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


class PersistenceClassifier(BaseEstimator, ClassifierMixin):
    """Probability of 'yes' = the latest known state (e.g. occupied an hour ago)."""

    def __init__(self, column: str = ""):
        self.column = column

    def fit(self, X: pd.DataFrame, y):
        self.classes_ = np.array([0, 1])
        self.fallback_ = float(np.mean(np.asarray(y, dtype=float)))
        return self

    def predict_proba(self, X: pd.DataFrame):
        v = X[self.column].to_numpy(dtype=float)
        p = np.clip(np.where(np.isfinite(v), v, self.fallback_), 0.0, 1.0)
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


class ShareOfOnes(BaseEstimator, ClassifierMixin):
    """Probability of 'yes' = how often it was 'yes' in training."""

    def fit(self, X, y):
        self.classes_ = np.array([0, 1])
        self.p_ = float(np.mean(np.asarray(y, dtype=float)))
        return self

    def predict_proba(self, X):
        return np.column_stack([np.full(len(X), 1 - self.p_), np.full(len(X), self.p_)])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


class ChangeRegressor(BaseEstimator, RegressorMixin):
    """Predict the change from an anchor input (the latest known target value), then add it back.

    Strong for slow-moving targets (CO2, temperatures) where "same as before" is hard to beat:
    the model only has to learn the departure from persistence.
    """

    def __init__(self, base=None, anchor: str = ""):
        self.base = base
        self.anchor = anchor

    def fit(self, X: pd.DataFrame, y):
        a = X[self.anchor].to_numpy(dtype=float)
        yy = np.asarray(y, dtype=float)
        self.mean_ = float(np.nanmean(yy))
        ok = np.isfinite(a) & np.isfinite(yy)
        self.base_ = clone(self.base).fit(X[ok], yy[ok] - a[ok])
        return self

    def predict(self, X: pd.DataFrame):
        a = X[self.anchor].to_numpy(dtype=float)
        return np.where(np.isfinite(a), a, self.mean_) + self.base_.predict(X)


class _IgnoreEmptyInputs:
    """For gradient boosting: inputs with no values at all in the training rows are left out.

    scikit-learn's histogram binning fails on a column that is entirely missing, which happens when a
    long gap in the data falls inside an early tuning fold. When every input has values, the data are
    passed through unchanged, so results are identical to the plain estimator.
    """

    def fit(self, X, y, **kwargs):
        values = X.to_numpy(dtype=float) if hasattr(X, "to_numpy") else np.asarray(X, dtype=float)
        used = ~np.all(np.isnan(values), axis=0)
        self.used_inputs_ = None if used.all() else used
        return super().fit(self._keep(X), y, **kwargs)

    def _keep(self, X):
        used = getattr(self, "used_inputs_", None)
        if used is None:
            return X
        return X.loc[:, used] if hasattr(X, "loc") else np.asarray(X)[:, used]

    def predict(self, X):
        return super().predict(self._keep(X))


class GradientBoostingRegressor(_IgnoreEmptyInputs, HistGradientBoostingRegressor):
    pass


class GradientBoostingClassifier(_IgnoreEmptyInputs, HistGradientBoostingClassifier):
    def predict_proba(self, X):
        return super().predict_proba(self._keep(X))


def scores(estimator, X: pd.DataFrame, task: str) -> np.ndarray:
    """Predicted values (regression) or predicted probability of 'yes' (classification)."""
    if task == "classification":
        proba = estimator.predict_proba(X)
        classes = list(getattr(estimator, "classes_", [0, 1]))
        return proba[:, classes.index(1)] if 1 in classes else np.zeros(len(X))
    return estimator.predict(X)


# ----- candidates -------------------------------------------------------------
def candidates(random_state: int = 0, task: str = "regression",
               anchor: Optional[str] = None) -> Dict[str, Tuple[Any, Dict[str, Any]]]:
    """Model name -> (estimator, hyperparameter search space).

    anchor: for forecasts, the column holding the latest known target value; adds "gbm_change",
    a gradient-boosting model of the change from that value.
    """
    if task == "classification":
        return {
            "logistic": (
                Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler()),
                          ("model", LogisticRegression(max_iter=2000))]),
                {"model__C": loguniform(1e-3, 1e3)},
            ),
            "random_forest": (
                Pipeline([("impute", SimpleImputer(strategy="median")),
                          ("model", RandomForestClassifier(n_estimators=150, n_jobs=-1,
                                                           random_state=random_state))]),
                {"model__max_depth": [None, 8, 16, 24], "model__min_samples_leaf": [1, 3, 10, 30],
                 "model__max_features": [1.0, 0.6, 0.3]},
            ),
            "gbm": (
                GradientBoostingClassifier(random_state=random_state),
                {"learning_rate": [0.05, 0.1, 0.2], "max_leaf_nodes": [7, 15, 31],
                 "min_samples_leaf": [20, 50, 100], "l2_regularization": [0.0, 0.1, 1.0],
                 "max_iter": [100, 200]},
            ),
        }
    pool = {
        "ridge": (
            Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler()), ("model", Ridge())]),
            {"model__alpha": loguniform(1e-3, 1e3)},
        ),
        "random_forest": (
            Pipeline([("impute", SimpleImputer(strategy="median")),
                      ("model", RandomForestRegressor(n_estimators=150, n_jobs=-1, random_state=random_state))]),
            {"model__max_depth": [None, 8, 16, 24], "model__min_samples_leaf": [1, 3, 10, 30],
             "model__max_features": [1.0, 0.6, 0.3]},
        ),
        "gbm": (
            GradientBoostingRegressor(random_state=random_state),
            {"learning_rate": [0.05, 0.1, 0.2], "max_leaf_nodes": [7, 15, 31],
             "min_samples_leaf": [20, 50, 100], "l2_regularization": [0.0, 0.1, 1.0],
             "max_iter": [100, 200]},
        ),
    }
    if anchor:
        pool["gbm_change"] = (
            ChangeRegressor(GradientBoostingRegressor(random_state=random_state), anchor),
            {"base__learning_rate": [0.05, 0.1, 0.2], "base__max_leaf_nodes": [7, 15, 31],
             "base__min_samples_leaf": [20, 50, 100], "base__l2_regularization": [0.0, 0.1, 1.0],
             "base__max_iter": [100, 200]},
        )
    return pool


DEFAULT_MODELS = {"regression": ("ridge", "random_forest", "gbm", "gbm_change"),
                  "classification": ("logistic", "random_forest", "gbm")}


def tune(estimator, space: Dict[str, Any], X: pd.DataFrame, y: pd.Series, gap_steps: int,
         n_iter: int, random_state: int, n_splits: int = 3,
         task: str = "regression") -> Tuple[Any, Dict[str, Any], Optional[float]]:
    """Random search with rolling-origin (time-ordered) cross-validation on the training set only."""
    if not space or n_iter <= 0:
        est = clone(estimator).fit(X, y)
        return est, {}, None
    cv = TimeSeriesSplit(n_splits=n_splits, gap=gap_steps)
    if task == "classification":
        # A fold whose training part holds one class only (e.g. a building closed for weeks) cannot be fitted.
        yv = np.asarray(y)
        cv = [(tr, te) for tr, te in cv.split(X) if len(np.unique(yv[tr])) == 2]
        if not cv:
            est = clone(estimator).fit(X, y)
            return est, {}, None
    scoring = "neg_brier_score" if task == "classification" else "neg_root_mean_squared_error"
    # Sequential search; forests parallelise internally with threads (process pools are slow to start on Windows).
    search = RandomizedSearchCV(clone(estimator), space, n_iter=n_iter, cv=cv, scoring=scoring,
                                random_state=random_state, refit=True, error_score="raise")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        search.fit(X, y)
    return search.best_estimator_, dict(search.best_params_), float(-search.best_score_)
