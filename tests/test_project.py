"""End to end: messy export -> checked model -> saved run -> deployment."""

import json

import pandas as pd
import pytest

import bemlops

FAST = dict(models=("ridge", "gbm"), n_iter=2)
TS = dict(timestamp="Timestamp", timestamp_format="%m/%d/%Y %I:%M:%S %p")


@pytest.fixture(scope="module")
def fitted(messy, tmp_path_factory):
    from bemlops.datasets import OFFICE_POINTS

    export, _ = messy
    p = bemlops.Project(export, "AHU1_CLG_KW", dict(OFFICE_POINTS), horizon="1h", name="test-run",
                        intended_use="Hour-ahead cooling power for demand response.", **TS)
    p.check_data()
    p.note("Test note.")
    p.prepare(freq="15min")
    results = p.fit(**FAST)
    folder = p.save_run(tmp_path_factory.mktemp("runs"))
    return p, results, folder


def test_forecast_beats_persistence(fitted):
    _, r, _ = fitted
    assert r.task["mode"] == "forecast" and r.task["horizon_steps"] == 4
    assert r.task["task_type"] == "regression"
    assert r.skill > 0.1  # against the strongest no-ML baseline (persistence, yesterday or daily profile)
    assert r.baseline_name in ("persistence", "same_time_yesterday", "same_time_last_week", "time_of_day_profile",
                               "time_of_week_profile", "towt")
    assert r.guideline14 is not None and "cvrmse_pct" in r.test
    assert r.backtest and len(r.backtest["blocks"]) == 3


def test_run_folder_is_complete_and_auditable(fitted):
    p, r, folder = fitted
    for name in ("report.md", "model_card.md", "run.json", "model.joblib", "test_predictions.csv"):
        assert (folder / name).exists(), name
    record = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    assert record["notes"] == ["Test note."]
    assert record["data"]["prepared_fingerprint"]
    assert record["chosen_model"]["name"] == r.chosen
    assert record["config"]["target"] == "AHU1_CLG_KW"
    assert record["unresolved_errors"] == []
    assert all(g["passed"] for g in record["gates"].values()), record["gates"]
    assert any(e["step"] == "mask_sentinels" for e in record["prepare"]["log"])
    assert "demand response" in (folder / "model_card.md").read_text(encoding="utf-8")


def test_deployed_model_forecasts_ahead_and_checks_drift(fitted):
    p, r, folder = fitted
    model = bemlops.load_model(folder / "model.joblib")
    recent = p.raw.loc[p.raw.index >= p.raw.index.max() - pd.Timedelta(days=10)]
    out = model.predict(recent, on_error="warn")
    future = out[out.index > recent.index.max()]
    assert len(future) == model.horizon and future["predicted"].notna().all()
    drift = model.check_drift(recent)
    assert drift.error_now > 0 and isinstance(drift.retrain_recommended, bool)


def test_live_data_with_wrong_units_is_refused(fitted):
    p, _, folder = fitted
    model = bemlops.load_model(folder / "model.joblib")
    bad = p.raw.loc[p.raw.index >= p.raw.index.max() - pd.Timedelta(days=10)].copy()
    # The outdoor-temperature feed switched to degC. Still a plausible outdoor value if read as degF
    # (a cold day), so only a comparison with the training data can catch it.
    bad["OAT"] = (pd.to_numeric(bad["OAT"].astype(str).str.replace(" °F", ""), errors="coerce") - 32) * 5 / 9
    with pytest.raises(bemlops.InvalidInputData, match="input_shift:OAT"):
        model.predict(bad)
    # A zone sensor that switched units is caught by the physics check itself.
    bad2 = p.raw.loc[p.raw.index >= p.raw.index.max() - pd.Timedelta(days=10)].copy()
    bad2["RM204_ZN_T"] = (bad2["RM204_ZN_T"] - 32) * 5 / 9
    with pytest.raises(bemlops.InvalidInputData, match="unit_mismatch:RM204_ZN_T"):
        model.predict(bad2)


def test_virtual_sensor_mode(messy):
    from bemlops.datasets import OFFICE_POINTS

    export, _ = messy
    p = bemlops.Project(export, "RM204_CO2", dict(OFFICE_POINTS), horizon=0, **TS)
    p.check_data()
    p.prepare(freq="15min")
    r = p.fit(**FAST)
    # The daily profile is a strong reference for CO2 in a scheduled office; with this tiny search the
    # framework may rightly keep the baseline (skill 0). What must hold: a valid estimate, target not an input.
    assert r.baseline_name in ("training_mean", "time_of_day_profile") and r.skill >= 0
    assert not any(f["source"] == "RM204_CO2" for f in r.features)


def test_yes_no_target_is_classification(messy, tmp_path):
    from bemlops.datasets import OFFICE_POINTS

    export, _ = messy
    p = bemlops.Project(export, "RM204_OCC_STS", dict(OFFICE_POINTS), horizon="1h", **TS)
    assert p.task == "classification"
    p.check_data()
    p.prepare(freq="15min")
    r = p.fit(models=("logistic", "gbm"), n_iter=2)
    assert r.baseline_name in ("persistence", "same_time_yesterday", "same_time_last_week",
                               "time_of_day_probability")
    assert {"brier", "accuracy", "roc_auc"} <= set(r.test)
    assert r.skill >= 0  # Brier skill score vs the strongest baseline (on this synthetic schedule, the profile)
    folder = p.save_run(tmp_path)
    out = bemlops.load_model(folder / "model.joblib").predict(p.raw.iloc[-3000:], on_error="warn")
    assert out["probability"].between(0, 1).all() and set(out["predicted"].unique()) <= {0, 1}


def test_intervals_drivers_and_provenance(fitted):
    p, r, folder = fitted
    iv = r.interval
    assert iv and iv["half_width"] > 0 and 0.7 <= iv["test_coverage"] <= 1.0
    assert {"lower", "upper"} <= set(r.predictions.columns)
    shares = [d["share"] for d in r.drivers]
    assert shares and 0.9 <= sum(shares) <= 1.0 + 1e-9  # tiny contributions (< 0.5%) are not listed
    assert any("AHU1_CLG_KW" in d["input"] for d in r.drivers[:3])  # its own recent history matters most
    record = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    assert len(record["run"]["environment"]["package_fingerprint"]) == 16
    out = bemlops.load_model(folder / "model.joblib").predict(p.raw.iloc[-3000:], on_error="warn")
    ok = out.dropna(subset=["predicted"])
    assert (ok["lower"] <= ok["predicted"]).all() and (ok["predicted"] <= ok["upper"]).all()


def test_holidays_become_a_known_ahead_input(messy):
    from bemlops.datasets import OFFICE_POINTS

    export, _ = messy
    p = bemlops.Project(export, "AHU1_CLG_KW", dict(OFFICE_POINTS), horizon="1h",
                        holidays=["2025-10-13", "2025-11-11"], **TS)
    p.check_data()
    p.prepare(freq="15min")
    r = p.fit(models=("ridge",), n_iter=1)
    assert "is_holiday" in r.model.feature_names and p.config()["holidays"] == ["2025-10-13", "2025-11-11"]


def test_extended_baselines_towt_and_time_of_week():
    """v0.3.0 baselines: a time-of-week profile, a time-of-week-and-temperature regression and, for yes/no
    targets, a time-of-day probability profile. TOWT must recover a load driven by schedule and temperature."""
    import numpy as np
    import pandas as pd

    from bemlops.models import ProbabilityProfile, TimeOfWeekProfile, TOWTBaseline

    idx = pd.date_range("2024-01-01", periods=24 * 7 * 8, freq="1h")
    rng = np.random.default_rng(0)
    temp = 15 + 10 * np.sin(2 * np.pi * np.arange(len(idx)) / (24 * 30)) + rng.normal(0, 1, len(idx))
    sched = np.where((idx.day_of_week < 5) & (idx.hour >= 8) & (idx.hour < 18), 50.0, 10.0)
    load = sched + 2.0 * np.maximum(temp - 18, 0) + rng.normal(0, 1, len(idx))
    X = pd.DataFrame({"oat": temp}, index=idx)
    y = pd.Series(load, index=idx)
    train, test = slice(0, 24 * 7 * 6), slice(24 * 7 * 6, None)
    towt = TOWTBaseline("oat").fit(X.iloc[train], y.iloc[train])
    tow = TimeOfWeekProfile().fit(X.iloc[train], y.iloc[train])
    rmse = lambda p: float(np.sqrt(np.mean((y.iloc[test].to_numpy() - p) ** 2)))  # noqa: E731
    assert rmse(towt.predict(X.iloc[test])) < 2.0                      # close to the noise level
    assert rmse(towt.predict(X.iloc[test])) < rmse(tow.predict(X.iloc[test]))
    occ = pd.Series((sched > 20).astype(int), index=idx)
    prob = ProbabilityProfile().fit(X.iloc[train], occ.iloc[train]).predict_proba(X.iloc[test])[:, 1]
    assert np.all((prob >= 0) & (prob <= 1))


def test_guideline14_is_reported_not_gated_for_forecasts():
    from bemlops.governance import check_gates as evaluate_gates

    record = {"unresolved_errors": [], "leakage_warnings": [], "split": {"sizes": {"test": 500}},
              "test": {"skill": 0.2, "guideline14": {"passes": False, "cvrmse_pct": 40.0, "nmbe_pct": 1.0,
                                                     "applies_as_gate": False}}}
    gates = evaluate_gates(record)
    assert gates["guideline14"]["passed"] and "not gated" in gates["guideline14"]["detail"]
    record["test"]["guideline14"]["applies_as_gate"] = True
    assert not evaluate_gates(record)["guideline14"]["passed"]


def test_towt_merges_sparse_temperature_segments():
    """A temperature segment with a handful of training hours must not get its own slope: in v0.3.0 such a
    segment made the fit unstable and one cross-validation fold produced errors of 400 kWh."""
    import numpy as np
    import pandas as pd

    from bemlops.models import TOWTBaseline

    idx = pd.date_range("2024-01-01", periods=24 * 7 * 6, freq="1h")
    rng = np.random.default_rng(1)
    temp = rng.normal(15, 3, len(idx))
    temp[:5] = -10.0                       # five cold hours: a sparse segment below the first knot
    load = 20 + 0.5 * temp + rng.normal(0, 1, len(idx))
    X, y = pd.DataFrame({"oat": temp}, index=idx), pd.Series(load, index=idx)
    m = TOWTBaseline("oat").fit(X.iloc[5:], y.iloc[5:])  # the cold hours are not in training
    assert all(k > -1.2 for k in m.knots_) and len(m.knots_) < len(TOWTBaseline.KNOTS_C)
    pred = m.predict(X.iloc[:5])
    assert np.all(np.abs(pred - load[:5]) < 25)   # no wild extrapolation
