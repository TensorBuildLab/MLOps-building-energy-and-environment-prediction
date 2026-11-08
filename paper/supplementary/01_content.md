# Problems found during the study and how they were fixed {-}

The framework was revised during the study in three rounds: a first version was run on the real datasets, an independent agent then reviewed the code with instructions only to find correctness problems, and the pilot agents of experiment E5 used it. Every problem found was fixed with a regression test. Table S1 lists the fixes included in the version used for every result in the paper (0.2.0.dev0, package fingerprint f394d2e9ee9047c8). Table S2 lists the changes made after the experiments; they are in release 0.2.0 but were not evaluated, with one exception: the three ROBOD chilled-water tasks re-run after the dead-meter correction used the gradient-boosting fix in Table S2 (package fingerprint 042ae8d1a30afc30). That fix cannot change any other result, because every earlier fit would have failed at the same point.

**Table S1.** Fixes made before the reported experiments.

| Found by | Problem | Fix |
|---|---|---|
| Real data (ROBOD) | Stuck-sensor runs and spikes were counted across gaps in the data (weekends missing) | Runs and spike windows never span a gap |
| Real data (ROBOD, Aalborg) | Solar, illuminance, PM2.5 and supply-air temperature were flagged for spikes that are real | Spike checks disabled for those quantities |
| Real data (ROBOD, Aalborg) | No way to state that a sensor's flat stretches are normal (CO2 floor at 400 ppm, change-of-value logging) | *flat_ok* declaration; the stuck warning recognises change-of-value logging from the share of unchanged steps |
| Real data | Day-of-year inputs were added with less than a year of history | Seasonal inputs only with a full year |
| Code review | Saving a run failed when the training period crossed a daylight-saving change | Fixed; test with Europe/Copenhagen data |
| Code review | Interval totals (energy) were too small when readings were missing, filling missing targets with zeros | Incomplete intervals become missing |
| Code review | Inputs constant in a short live window were dropped and imputed in serving | Serving always builds every trained input |
| Code review | Known-ahead inputs (forecasts, schedules) were empty in the live forecast rows | *future_inputs* argument; rows with imputed inputs are flagged |
| Code review | Decimal commas (*21,5*) were truncated to 21 | Reported as an error, never guessed |
| Code review | A guessed timestamp format could silently drop half the rows and swap day and month | More than 1% unreadable timestamps stops the project |
| Code review | Acceptances carried into automated retraining approved new, different errors | Earlier acceptances never approve errors on new data |
| Code review | Guideline 14 "passed" for meters with a negative mean | Not passable for a non-positive mean |
| Code review | Champion/challenger comparison included rows inside the horizon gap | Rows start after both training periods plus the horizon |
| Code review | Live data in a different time zone was accepted | Time zone checked against training |
| Pilot agents and code review | Cleaning decisions looked ahead: centred spike windows; stuck stretches masked from their start | Causal cleaning: spikes judged against earlier readings, stuck stretches masked from the moment they are detectable |
| Pilot agents | Timestamps whose UTC offset changes at daylight saving raised a bare pandas error | *tz=* option; offsets parsed and converted to the building's zone |
| Pilot agents | A unit switch part-way through a series was reported only as "out of range" | The switch time and the likely unit are reported |
| Pilot agents | Persistence is a weak reference for scheduled loads, which flatters skill | Time-of-day profile baseline; skill against the strongest baseline |
| Pilot agents | One test period decided the verdict, though a single period can be unusual | Rolling-origin backtest over three later blocks |
| Pilot agents | No way to add the agent's own model; no "change from the last value" model | *custom_models* hook; *gbm_change* candidate |
| Pilot agents | No range on forecasts; no view of what the model relies on | 90% prediction intervals with test coverage; grouped input drivers |

**Table S2.** Changes made after the reported experiments (not evaluated in the paper).

| Found by | Problem | Fix |
|---|---|---|
| Pilot agents | The deployed model never trained on the most recent (test) period | *refit_all* option: after evaluation, refit the chosen configuration on all data for deployment, recorded as such |
| Pilot agents | Missing quantities: VOC, sound level, barometric pressure, water flow | Added |
| Pilot agents | Saved forests predicted in parallel threads, so repeated forecasts differed by about 1e-15 | Saved models predict single-threaded and repeat exactly |
| Lifecycle experiment (E4) | Monitoring compared a model only with its own test-time error, so a model worse than persistence (district heating in summer) was never flagged | Drift checks also score the baseline on the same recent rows and recommend falling back to it |
| Case-study re-run (ROBOD Room 3, after the dead-meter mask) | Gradient boosting crashed when an input had no values at all in an early tuning fold | Such inputs are left out of that fit; otherwise identical to the plain estimator (test added) |
| Pilot agents (T2) | A meter reading zero while the equipment it measures is running is not flagged by any single-column check | Not fixed in the package; the case-study loader masks such days, and the skill asks the agent to look for contradictions between related points |

# Package modules {-}

**Table S3.** Modules of the bemlops package (evaluated version 0.2.0.dev0, 24 physical quantities; release 0.2.0 has 28).

| Module | Role |
|---|---|
| *quantities*, *schema* | 24 physical quantities with units, conversions, plausible and typical ranges, and flags; parsing of declarations |
| *cleaning*, *checks* | Causal detectors for export and sensor problems; the data report with blocking errors |
| *prepare* | Logged standard preparation and resampling |
| *features*, *split* | Inputs shifted by the horizon, with an audit; time-ordered splits with a gap |
| *models*, *metrics* | Baselines (persistence, same time yesterday, time-of-day profile, mean, share of ones) and tuned candidates; RMSE, MAE, CV(RMSE), NMBE, Guideline 14, Brier score, accuracy, balanced accuracy, F1, ROC AUC |
| *project* | The workflow, its configuration, backtest, intervals and input drivers |
| *report*, *governance* | Run record, report, model card; promotion gates |
| *deploy*, *registry*, *pipeline*, *cli* | Deployable model with live validation and drift checks; registry with stages, champion/challenger and rollback; scheduled pipelines; command line |

# Evaluation protocol per task {-}

**Table S4.** RMSE of the same random forest on the same rows under each protocol, in the unit of each target. The time-ordered holdout scores a different, later window and is shown for reference only.

<!-- table: s_protocol_tasks -->

# Lifecycle experiment by month {-}

**Table S5.** District-heating power 1 h ahead: monthly RMSE (kW) of each arm. "(P)": months in which the fallback rule would have served persistence. Drift ratio: recent error divided by the error at test time.

<!-- table: s_lifecycle_dh -->

**Table S6.** Room A CO~2~ 1 h ahead: monthly RMSE (ppm) of each arm, as in Table S5.

<!-- table: s_lifecycle_co2 -->

# Results of every task {-}

**Table S7.** Chosen model, reference baseline, test skill, backtest skill, coverage of the 90% interval and gate decision for each of the 92 tasks. Skill is defined on RMSE (Brier score for binary targets) against the reference baseline; a chosen baseline has skill 0 by definition.

<!-- table: s_all_tasks -->

# Pilot materials {-}

The launch prompts of the eight pilot agents, the code and reports they delivered (without data or model binaries), the manual audit and the hidden-period scores are in the benchmarks/pilot folder of the repository (https://github.com/TensorBuildLab/MLOps-building-energy-and-environment-prediction). The task descriptions are generated by benchmarks/pilot/make_tasks.py, and the deliverables can be re-scored with benchmarks/pilot/score.py.
