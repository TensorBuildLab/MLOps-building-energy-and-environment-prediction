# MLOps compliance

How `bemlops` follows MLOps, checked against two references:

1. The nine principles and nine technical components in Kreuzberger, Kühl
   and Hirschl, *Machine Learning Operations (MLOps): Overview, Definition,
   and Architecture*, IEEE Access 11 (2023) 31866–31879,
   doi:10.1109/ACCESS.2023.3262138.
2. The MLOps lifecycle used in the 2024 preliminary paper (data preparation
   through monitoring). The 2024 work stopped before deployment; this package
   covers the whole cycle.

Each row names the code that implements it and the test that checks it.
**Full** means implemented and tested. **Partial** means part of it is
implemented and the rest is stated.

## Principles

| Principle | Status | How | Evidence |
|---|---|---|---|
| P1 CI/CD automation | Full for code and models; partial for package release | Every push runs the test suite, including end-to-end model tests, on Linux and Windows (`.github/workflows/tests.yml`). Models are delivered through gated promotion (`Registry.promote`, `bemlops train --promote`). There is no automated PyPI release yet. | `tests/`, `test_mlops.py::test_failed_gates_block_promotion_unless_forced` |
| P2 Workflow orchestration | Full (via your scheduler) | `bemlops.train` / `retrain` / `reproduce` and the `bemlops` command line are single-call pipelines with exit codes, built to be run by cron, Airflow or GitHub Actions. There is no built-in scheduler, by design. | `test_mlops.py::test_cli_monitor_and_predict` |
| P3 Reproducibility | Full | Every run stores its full configuration, data fingerprints, random seeds, library versions and code commit (`run.json`). `bemlops.reproduce` re-runs it and checks that the data and every metric match exactly. | `test_mlops.py::test_run_reproduces_exactly` |
| P4 Versioning of data, code, model | Full for code and model; partial for data | Code: git commit recorded in every run. Model: numbered versions in the registry. Data: content fingerprints of the raw and prepared data. Raw data is not stored by the package; keep it in your own storage or a data-versioning tool. | `run.json` → `data`, `run.environment.code_commit`; `registry.json` |
| P5 Collaboration | Full | Human-readable `report.md` and `model_card.md` for every run; decisions (`note`) and accepted issues (with required reasons) are recorded. The agent skill makes the AI agent's work reviewable the same way. | `test_project.py::test_run_folder_is_complete_and_auditable` |
| P6 Continuous ML training & evaluation | Full | `bemlops.retrain` trains a challenger on newer data with the production configuration, scores champion and challenger on the same unseen rows, and promotes only if the challenger passes the gates and wins. | `test_mlops.py::test_retrain_compares_on_unseen_data_and_logs_everything` |
| P7 ML metadata tracking / logging | Full | `run.json` (data check, decisions, preparation log, features, split, validation table, test results, gates, event log) and `registry.json` (versions, stages, every register / promote / compare / rollback event). | same as above |
| P8 Continuous monitoring | Full | Every live prediction re-runs the training-time data checks plus a training-vs-live comparison, and refuses bad data (`InvalidInputData`). `check_drift` tracks accuracy against the test-time level, inputs outside the training range, and new sensor faults. | `test_project.py::test_live_data_with_wrong_units_is_refused`, `test_deployed_model_forecasts_ahead_and_checks_drift` |
| P9 Feedback loops | Full | Monitoring → `retrain_recommended` (command-line exit code 2) → retrain → champion/challenger → promote or keep. Data checks → agent fix or accept-with-reason → re-check. | `cli.py`, `pipeline.py` |

## Technical components

| Component | Status | In bemlops |
|---|---|---|
| C1 CI/CD component | Full | GitHub Actions for code; promotion gates for models |
| C2 Source code repository | Full | This Git repository; the commit is recorded in each run |
| C3 Workflow orchestration component | Full (via your scheduler) | `pipeline.py`, `cli.py` |
| C4 Feature store system | Not included, on purpose | Features are rebuilt from the declared configuration in training and in serving by the same code (`build_features`), which removes the training-serving skew a feature store guards against at this scale. A shared feature store matters for large portfolios and is future work. |
| C5 Model training infrastructure | Full | scikit-learn on any machine; time-ordered cross-validation for tuning |
| C6 Model registry | Full | `registry.py`: versions, stages, gates, compare, rollback |
| C7 ML metadata stores | Full (file-based) | `run.json`, `registry.json` |
| C8 Model serving component | Partial | Batch and scheduled serving (`ForecastModel.predict`, `bemlops predict`). No HTTP service yet; one can wrap `predict` in a few lines. |
| C9 Monitoring component | Full | `check_drift`, live validation, `bemlops monitor` |

## Lifecycle stages (2024 paper, now completed)

| Stage | 2024 prompt template | bemlops |
|---|---|---|
| Data preparation | LLM-written code, unchecked | Data checks with blocking errors; logged standard preparation |
| Feature engineering | Selection on the full dataset (leakage) | Lags that never reach into the future; audited; near-copies of the target flagged |
| Data splitting | Random 80/10/10 split (leakage) | Time-ordered with a horizon-length gap; no random split exists |
| Model selection & training | Linear regression, random forest | Baselines plus ridge / logistic, random forest, gradient boosting, for numeric and yes/no targets |
| Hyperparameter tuning | Grid search, shuffled CV | Random search with time-ordered cross-validation on the training set only |
| Evaluation | MSE | Skill vs baseline; Guideline 14; MAE in physical units; Brier, accuracy, F1, ROC AUC for yes/no |
| Deployment | Not covered | Saved model; registry; gated promotion |
| Inference | Not covered | Live prediction with input validation; same preparation as training |
| Monitoring | Not covered | Drift and data-quality monitoring; retraining loop |

## Running it on a schedule

A weekly monitoring and retraining job, for example with cron:

```bash
# Mondays 06:00: check the production model on the last 14 days; retrain if needed.
0 6 * * 1  bemlops monitor --registry models --name ahu1-kw --data last14d.csv || \
           bemlops retrain --registry models --name ahu1-kw --data history.csv
```

`bemlops monitor` exits with 0 when no action is needed and 2 when retraining
is recommended. `bemlops retrain` promotes the new model only if it passes the
gates and beats the current one on data neither has trained on.
