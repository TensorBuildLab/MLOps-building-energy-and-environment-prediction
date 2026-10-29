## 4. Implementation

`bemlops` is a Python package (BSD 3-Clause licence) built on pandas and
scikit-learn. Table 4 lists its modules. A typical session takes about a
dozen lines:

```python
p = bemlops.Project(df, target="AHU1_CLG_KW", horizon="1h", tz="America/Phoenix", columns={
        "AHU1_CLG_KW": "electric_power [kW]",
        "OAT": "outdoor_air_temperature [degF]",
        "RM204_ZN_T": "zone_air_temperature [degF]", ...})
print(p.check_data())          # issues, with severities and suggested fixes
p.prepare(freq="15min")        # logged, causal standard preparation
results = p.fit()              # baselines + tuned models, time-ordered, backtest, intervals
folder = p.save_run("runs/")   # record, report, model card, model
reg = bemlops.Registry("models/")
reg.promote(p.name, reg.register(folder)["version"], reason="...")  # gates checked here
```

**Table 4.** Package modules (version 0.2.0.dev0).

| Module | Role |
|---|---|
| `quantities`, `schema` | 24 physical quantities with units, conversions, plausible and typical ranges, and flags; parsing of declarations |
| `cleaning`, `checks` | Causal detectors for export and sensor problems; the data report with blocking errors |
| `prepare` | Logged standard preparation and resampling |
| `features`, `split` | Inputs shifted by the horizon, with an audit; time-ordered splits with a gap |
| `models`, `metrics` | Baselines (persistence, same time yesterday, time-of-day profile, mean, share of ones) and tuned candidates; RMSE, MAE, CV(RMSE), NMBE, Guideline 14, Brier score, accuracy, balanced accuracy, F1, ROC AUC |
| `project` | The workflow, its configuration, backtest, intervals and input drivers |
| `report`, `governance` | Run record, report, model card; promotion gates |
| `deploy`, `registry`, `pipeline`, `cli` | Deployable model with live validation and drift checks; registry with stages, champion/challenger and rollback; scheduled pipelines; command line |

The candidate models are deliberately conventional, and the hyperparameter
searches in the case studies are small (3–6 settings per model). The
framework's claims concern the process around the model, not the model
family. A model can be added through a `custom_models` argument in a few
lines.

The evaluated version has 43 automated tests. They include:
- a test that perturbs every value after the forecast time and checks that no
  input changes;
- tests that every planted fault in a synthetic export is detected;
- regression tests for each defect in Appendix A;
- tests of the full registry, retraining and reproduction loop.

Every run record carries:
- the git commit of the case-study code;
- a fingerprint of the package source, so that runs made at different case-study
  commits can be shown to use identical package code.
