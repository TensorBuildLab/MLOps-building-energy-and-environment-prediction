"""MLOps lifecycle: registry, promotion gates, champion/challenger retraining, reproduction, CLI."""

import json

import pandas as pd
import pytest

import bemlops
from bemlops.datasets import OFFICE_POINTS, messy_office

FAST = {"models": ["ridge", "gbm"], "n_iter": 2, "fractions": [0.7, 0.15, 0.15], "random_state": 0}
TS = dict(timestamp="Timestamp", timestamp_format="%m/%d/%Y %I:%M:%S %p")


@pytest.fixture(scope="module")
def config():
    export, _ = messy_office(days=45, seed=3)
    p = bemlops.Project(export, "AHU1_CLG_KW", dict(OFFICE_POINTS), horizon="1h", name="ahu1-kw", **TS)
    p.prepare(freq="15min")
    p.fit_options = dict(FAST)
    return p.config()


@pytest.fixture(scope="module")
def lifecycle(config, tmp_path_factory):
    root = tmp_path_factory.mktemp("mlops")
    reg = bemlops.Registry(root / "registry")
    early, _ = messy_office(days=45, seed=3)
    first = bemlops.train(early, config, root / "runs", reg)
    reg.promote("ahu1-kw", first.registry_entry["version"], reason="First production model.")
    later, _ = messy_office(days=75, seed=3)  # the same building, 30 more days of data
    outcome = bemlops.retrain(later, reg, "ahu1-kw", root / "runs")
    return reg, first, outcome, early


def test_registered_with_gates(lifecycle):
    reg, first, _, _ = lifecycle
    e = first.registry_entry
    assert e["version"] == 1 and e["gates_passed"]
    assert set(e["gates"]) == {"data_check_resolved", "beats_baseline", "guideline14",
                               "no_suspicious_inputs", "enough_test_data"}


def test_retrain_compares_on_unseen_data_and_logs_everything(lifecycle):
    reg, _, outcome, _ = lifecycle
    cmp_ = outcome["comparison"]
    assert outcome["challenger_version"] == 2 and cmp_["rows"] >= 50
    assert pd.Timestamp(cmp_["from"]) >= pd.Timestamp(reg.load("ahu1-kw", 1).train_end)
    assert outcome["promoted"] == (outcome["gates_passed"] and cmp_["challenger_better"])
    actions = [e["action"] for e in reg.events("ahu1-kw")]
    assert actions[:3] == ["register", "promote", "register"] and "compare" in actions
    assert (reg.production("ahu1-kw")["version"] == 2) == outcome["promoted"]


def test_failed_gates_block_promotion_unless_forced(lifecycle, tmp_path):
    reg, first, _, _ = lifecycle
    strict = bemlops.Registry(tmp_path / "strict", policy=bemlops.PromotionPolicy(min_skill=0.99))
    entry = strict.register(first.run_folder, "ahu1-kw")
    assert not entry["gates_passed"]
    with pytest.raises(bemlops.PromotionRefused, match="beats_baseline"):
        strict.promote("ahu1-kw", entry["version"])
    with pytest.raises(ValueError):
        strict.promote("ahu1-kw", entry["version"], force=True, reason="")
    strict.promote("ahu1-kw", entry["version"], force=True, reason="Pilot only, owner signed off on 2026-10-29.")
    assert strict.events("ahu1-kw")[-1]["forced"] is True


def test_rollback(lifecycle):
    reg, _, _, _ = lifecycle
    reg.rollback("ahu1-kw", 1, reason="Testing rollback to the first model.")
    assert reg.production("ahu1-kw")["version"] == 1
    assert reg.events("ahu1-kw")[-1]["action"] == "rollback"


def test_run_reproduces_exactly(lifecycle):
    _, first, _, early = lifecycle
    res = bemlops.reproduce(first.run_folder / "run.json", early)
    assert res["data_matches"] and res["same_model"] and res["metrics_match"], res


def test_cli_monitor_and_predict(lifecycle, tmp_path):
    from bemlops.cli import main

    reg, _, _, early = lifecycle
    csv = tmp_path / "recent.csv"
    early.iloc[-4000:].to_csv(csv, index=False)
    out = tmp_path / "forecast.csv"
    assert main(["predict", "--registry", str(reg.root), "--name", "ahu1-kw", "--data", str(csv),
                 "--out", str(out), "--warn"]) == 0
    assert len(pd.read_csv(out)) > 100
    assert main(["monitor", "--registry", str(reg.root), "--name", "ahu1-kw", "--data", str(csv)]) in (0, 2)


def test_accepted_errors_are_not_carried_into_new_data(config):
    cfg = dict(config)
    cfg["accepted"] = {"columns:missing": "RH sensor removed in 2024; documented by facilities."}
    export, _ = messy_office(days=45, seed=5)
    p = bemlops.Project.from_config(export.drop(columns=["OAT"]), cfg)
    assert "columns:missing" in [i.id for i in p.unresolved()]  # must be decided again
    assert p.previous_acceptances
