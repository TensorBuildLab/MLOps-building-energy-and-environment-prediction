"""Guardrails: nothing from the future may reach a model input or a training set."""

import numpy as np
import pandas as pd
import pytest

import bemlops
from bemlops.features import Feature, LeakageError, audit, build_features
from bemlops.prepare import PrepareOptions, prepare
from bemlops.schema import parse_columns
from bemlops.split import time_split

STEP = pd.Timedelta("15min")


def _frame(n=3000, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2025-03-01", periods=n, freq=STEP)
    return pd.DataFrame({"y": rng.normal(size=n).cumsum(), "x": rng.normal(size=n),
                         "fc": rng.normal(size=n)}, index=idx)


SPECS = parse_columns({"y": "other", "x": "other",
                       "fc": {"quantity": "other", "known_ahead": True}})


@pytest.mark.parametrize("h", [1, 4, 96])
def test_changing_the_future_does_not_change_inputs(h):
    """Perturb every measured value after the forecast time; the input row must not move."""
    data = _frame()
    X, _, feats = build_features(data, "y", SPECS, h, STEP)
    audit(feats, "y", h)
    t = data.index[2000]
    origin = t - h * STEP
    changed = data.copy()
    later = changed.index > origin
    changed.loc[later, ["y", "x"]] += 1000.0
    X2, _, _ = build_features(changed, "y", SPECS, h, STEP)
    measured = [f.name for f in feats if f.kind != "known_ahead"]
    pd.testing.assert_series_equal(X.loc[t, measured], X2.loc[t, measured])


def test_estimation_mode_never_uses_the_target():
    X, _, feats = build_features(_frame(), "y", SPECS, 0, STEP)
    assert all(f.source != "y" for f in feats)
    assert "x" in X.columns  # same-moment inputs are the point of a virtual sensor


def test_audit_refuses_future_inputs():
    with pytest.raises(LeakageError):
        audit([Feature("x", "x", 0, "concurrent")], "y", horizon=4)
    with pytest.raises(LeakageError):
        audit([Feature("y__t-1", "y", 1, "target_lag")], "y", horizon=4)


def test_split_is_time_ordered_with_gap():
    idx = pd.date_range("2025-01-01", periods=1000, freq=STEP)
    sp = time_split(idx, gap=4 * STEP)
    tr, va, te = idx[sp.train], idx[sp.val], idx[sp.test]
    assert tr.max() + 4 * STEP < va.min() and va.max() + 4 * STEP < te.min()


def test_no_random_split_anywhere():
    import bemlops.split as split_module

    assert not any("random" in name.lower() or "shuffle" in name.lower() for name in dir(split_module))


def test_target_is_never_filled_and_inputs_fill_forward_only():
    idx = pd.date_range("2025-01-01", periods=400, freq=STEP)
    df = pd.DataFrame({"y": np.arange(400.0), "x": np.arange(400.0)}, index=idx)
    df.iloc[100:102] = np.nan  # a 30-minute hole in both
    out, _ = prepare(df, parse_columns({"y": "other", "x": "other"}), "y", PrepareOptions(fill_limit="1h"))
    assert out["y"].iloc[100:102].isna().all()
    assert (out["x"].iloc[100:102] == 99.0).all()  # last known value, not the future one


def test_fit_refuses_until_errors_are_dealt_with(messy, points):
    export, _ = messy
    points["RM204_ZN_T"] = "zone_air_temperature [degC]"
    p = bemlops.Project(export, "AHU1_CLG_KW", points, horizon="1h", timestamp="Timestamp",
                        timestamp_format="%m/%d/%Y %I:%M:%S %p")
    with pytest.raises(bemlops.UnresolvedIssues, match="unit_mismatch:RM204_ZN_T"):
        p.fit()
    with pytest.raises(ValueError, match="reason"):
        p.accept("unit_mismatch:RM204_ZN_T", reason="ok")


def test_cleaning_is_causal():
    """Found by the pilot agents and the code review: masking decisions must not depend on later data."""
    rng = np.random.default_rng(3)
    idx = pd.date_range("2025-01-01", periods=3000, freq="5min")
    x = pd.Series(20 + np.cumsum(rng.normal(0, 0.05, 3000)), index=idx)
    x.iloc[1500] += 8.0  # a spike
    x.iloc[2000:2200] = x.iloc[2000]  # stuck for ~16 h
    specs = parse_columns({"x": "zone_air_temperature [degC]", "y": "other"})
    base = pd.DataFrame({"x": x, "y": np.arange(3000.0)}, index=idx)
    out1, _ = prepare(base, specs, "y", PrepareOptions(freq="5min", fill_limit=None))
    cut = idx[2100]
    changed = base.copy()
    changed.loc[changed.index > cut, "x"] = 1000.0 * rng.random(int((changed.index > cut).sum()))
    out2, _ = prepare(changed, specs, "y", PrepareOptions(freq="5min", fill_limit=None))
    past = out1.index <= cut
    pd.testing.assert_series_equal(out1.loc[past, "x"], out2.loc[past, "x"])
    assert np.isnan(out1["x"].iloc[1500])  # the spike is still caught


def test_negative_horizon_and_live_constant_inputs():
    with pytest.raises(LeakageError):
        build_features(_frame(), "y", SPECS, -1, STEP)
    data = _frame()
    data["x"] = 1.0  # constant in this window
    X, _, _ = build_features(data, "y", SPECS, 4, STEP, target_lags=[4, 5], drop_constant=False)
    assert "x__t-4" in X.columns and X["x__t-4"].notna().any()


def test_gradient_boosting_ignores_an_input_with_no_values_in_a_fold():
    """A long gap can leave an input entirely missing in an early tuning fold (ROBOD Room 3 after the
    dead-meter days were masked); gradient boosting must skip that input instead of crashing, and must
    behave exactly like the plain estimator when every input has values."""
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import HistGradientBoostingRegressor

    from bemlops.models import GradientBoostingRegressor, tune

    rng = np.random.default_rng(0)
    X = pd.DataFrame({"a": rng.normal(size=400), "b": rng.normal(size=400)})
    y = pd.Series(2 * X["a"] + rng.normal(scale=0.1, size=400))
    X.loc[:199, "b"] = np.nan  # empty in the first half, so in the first folds
    best, params, _ = tune(GradientBoostingRegressor(random_state=0), {"max_iter": [50]}, X, y, gap_steps=1,
                           n_iter=1, random_state=0, task="regression")
    assert np.isfinite(best.predict(X)).all()
    full = X.fillna(0.0)
    ours = GradientBoostingRegressor(random_state=0, max_iter=50).fit(full, y).predict(full)
    plain = HistGradientBoostingRegressor(random_state=0, max_iter=50).fit(full, y).predict(full)
    assert np.array_equal(ours, plain)
