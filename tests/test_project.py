"""End to end: messy export -> checked model -> saved run -> deployment."""

import json

import pandas as pd
import pytest

import bemlops

FAST = dict(models=("ridge", "gbm"), n_iter=2)


@pytest.fixture(scope="module")
def fitted(messy, tmp_path_factory):
    from bemlops.datasets import OFFICE_POINTS

    export, _ = messy
    p = bemlops.Project(export, "AHU1_CLG_KW", dict(OFFICE_POINTS), horizon="1h", timestamp="Timestamp",
                        timestamp_format="%m/%d/%Y %I:%M:%S %p", name="test-run")
    p.check_data()
    p.note("Test note.")
    p.prepare(freq="15min")
    results = p.fit(**FAST)
    folder = p.save_run(tmp_path_factory.mktemp("runs"))
    return p, results, folder


def test_forecast_beats_persistence(fitted):
    _, r, _ = fitted
    assert r.task["mode"] == "forecast" and r.task["horizon_steps"] == 4
    assert r.skill > 0.2
    assert r.guideline14 is not None and "cvrmse_pct" in r.test


def test_run_folder_is_complete_and_auditable(fitted):
    p, r, folder = fitted
    for name in ("report.md", "run.json", "model.joblib", "test_predictions.csv"):
        assert (folder / name).exists(), name
    record = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    assert record["notes"] == ["Test note."]
    assert record["data"]["prepared_fingerprint"]
    assert record["chosen_model"]["name"] == r.chosen
    assert any(e["step"] == "mask_sentinels" for e in record["prepare"]["log"])


def test_deployed_model_forecasts_ahead_and_checks_drift(fitted):
    p, r, folder = fitted
    model = bemlops.load_model(folder / "model.joblib")
    recent = p.raw.loc[p.raw.index >= p.raw.index.max() - pd.Timedelta(days=10)]
    out = model.predict(recent)
    future = out[out.index > recent.index.max()]
    assert len(future) == model.horizon and future["predicted"].notna().all()
    drift = model.check_drift(recent)
    assert drift.rmse_now > 0 and isinstance(drift.retrain_recommended, bool)


def test_virtual_sensor_mode(messy):
    from bemlops.datasets import OFFICE_POINTS

    export, _ = messy
    p = bemlops.Project(export, "RM204_CO2", dict(OFFICE_POINTS), horizon=0, timestamp="Timestamp",
                        timestamp_format="%m/%d/%Y %I:%M:%S %p")
    p.check_data()
    p.prepare(freq="15min")
    r = p.fit(**FAST)
    assert r.baseline_name == "training_mean" and r.skill > 0.3
    assert not any(f["source"] == "RM204_CO2" for f in r.features)
