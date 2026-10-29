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
