## 4. Implementation

`bemlops` is a Python package (BSD 3-Clause licence) built on pandas and
scikit-learn. Table 3 lists its modules. A typical session is a dozen lines:

```python
p = bemlops.Project(df, target="AHU1_CLG_KW", horizon="1h", columns={
        "AHU1_CLG_KW": "electric_power [kW]",
        "OAT": "outdoor_air_temperature [degF]",
        "RM204_ZN_T": "zone_air_temperature [degF]", ...})
print(p.check_data())          # issues, with severities and fixes
p.prepare(freq="15min")        # logged standard preparation
results = p.fit()              # baselines + tuned models, time-ordered
folder = p.save_run("runs/")   # report, model card, record, model
reg = bemlops.Registry("models/")
reg.promote(p.name, reg.register(folder)["version"], reason="...")
```

**Table 3.** Package modules.

| Module | Role |
|---|---|
| `quantities`, `schema` | 26 physical quantities with units, conversions and plausible ranges; parsing of declarations such as `"zone_air_temperature [degF]"` |
| `cleaning`, `checks` | Detectors for export and sensor problems; the data report with blocking errors |
| `prepare` | Logged standard preparation |
| `features`, `split` | Leakage-safe inputs with an audit; time-ordered splits with a gap |
| `models`, `metrics` | Baselines and tuned candidates for regression (ridge, random forest, gradient boosting) and classification (logistic regression, random forest, gradient boosting); RMSE, MAE, CV(RMSE), NMBE, Guideline 14, Brier score, accuracy, balanced accuracy, F1, ROC AUC |
| `project` | The workflow and its configuration |
| `report`, `governance` | Run record, report, model card; promotion gates |
| `deploy`, `registry`, `pipeline`, `cli` | Deployable model with live validation and drift checks; registry with stages, champion/challenger and rollback; scheduled pipelines |

The candidate models are deliberately conventional. The framework's claims
concern the process around the model, not the model family, and a model
family can be added in a few lines. The package has 38 automated tests,
including tests that perturb every value after the forecast time and check
that no input changes, tests that every planted fault in a synthetic export
is detected, and tests of the full registry, retraining and reproduction loop.
