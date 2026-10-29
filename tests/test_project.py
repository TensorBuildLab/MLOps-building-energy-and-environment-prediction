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
    assert r.skill > 0.2
    assert r.guideline14 is not None and "cvrmse_pct" in r.test


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
    assert r.baseline_name == "training_mean" and r.skill > 0.3
    assert not any(f["source"] == "RM204_CO2" for f in r.features)


def test_yes_no_target_is_classification(messy, tmp_path):
    from bemlops.datasets import OFFICE_POINTS

    export, _ = messy
    p = bemlops.Project(export, "RM204_OCC_STS", dict(OFFICE_POINTS), horizon="1h", **TS)
    assert p.task == "classification"
    p.check_data()
    p.prepare(freq="15min")
    r = p.fit(models=("logistic", "gbm"), n_iter=2)
    assert r.baseline_name == "persistence"
    assert {"brier", "accuracy", "roc_auc"} <= set(r.test)
    assert r.skill > 0.2  # Brier skill score vs "same as an hour ago"
    folder = p.save_run(tmp_path)
    out = bemlops.load_model(folder / "model.joblib").predict(p.raw.iloc[-3000:], on_error="warn")
    assert out["probability"].between(0, 1).all() and set(out["predicted"].unique()) <= {0, 1}
