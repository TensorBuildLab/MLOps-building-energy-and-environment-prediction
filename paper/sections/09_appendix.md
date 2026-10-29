## Appendix A. Problems found by the evaluation, and how they were fixed

The framework was revised during this study in three rounds:
1. A first version was run on the real datasets.
2. An independent agent reviewed it, with instructions only to find
   correctness problems in the code.
3. The pilot agents of E5 used it.

Every problem found was fixed with a regression test. Most were invisible on
synthetic data. Table A1 lists the fixes in the version used for every
result in Section 6 (0.2.0.dev0, fingerprint `f394d2e9ee9047c8`). Table A2
lists the changes made after the experiments. Those changes are in the
released code but were not evaluated, with one exception: the three ROBOD
chilled-water tasks that were re-run after the dead-meter mask used the
boosting fix in Table A2. That fix cannot change any other result, because
every earlier fit of these models would have failed at the same point.

**Table A1.** Fixes before the reported experiments.

| Found by | Problem | Fix |
|---|---|---|
| Real data (ROBOD) | Stuck-sensor runs and spikes were counted across gaps in the data (weekends missing) | Runs and spike windows never span a gap |
| Real data (ROBOD, Aalborg) | Solar, illuminance, PM2.5 and supply-air temperature were flagged for spikes that are real | Spike checks disabled for those quantities |
| Real data (ROBOD, Aalborg) | No way to state that a sensor's flat stretches are normal (CO2 floor at 400 ppm, change-of-value logging) | `flat_ok` declaration; the stuck warning recognises change-of-value logging from the share of unchanged steps |
| Real data | Day-of-year inputs were added with less than a year of history | Seasonal inputs only with a full year |
| Code review | Saving a run failed when the training period crossed a daylight-saving change | Fixed; test with Europe/Copenhagen data |
| Code review | Interval totals (energy) were too small when readings were missing, filling missing targets with zeros | Incomplete intervals become missing |
| Code review | Inputs constant in a short live window were dropped and imputed in serving | Serving always builds every trained input |
| Code review | Known-ahead inputs (forecasts, schedules) were empty in the live forecast rows | `future_inputs` argument; rows with imputed inputs are flagged |
| Code review | Decimal commas (`21,5`) were truncated to 21 | Reported as an error, never guessed |
| Code review | A guessed timestamp format could silently drop half the rows and swap day and month | More than 1% unreadable timestamps stops the project |
| Code review | Acceptances carried into automated retraining approved new, different errors | Earlier acceptances never approve errors on new data |
| Code review | Guideline 14 "passed" for meters with a negative mean | Not passable for a non-positive mean |
| Code review | Champion/challenger comparison included rows inside the horizon gap | Rows start after both training periods plus the horizon |
| Code review | Live data in a different time zone was accepted | Time zone checked against training |
| Pilot agents and code review | Cleaning decisions looked ahead: centred spike windows; stuck stretches masked from their start | Causal cleaning: spikes judged against earlier readings, stuck stretches masked from the moment they are detectable |
| Pilot agents | Timestamps whose UTC offset changes at daylight saving raised a bare pandas error | `tz=` option; offsets parsed and converted to the building's zone |
| Pilot agents | A unit switch part-way through a series was reported only as "out of range" | The switch time and the likely unit are reported |
| Pilot agents | Persistence is a weak reference for scheduled loads, which flatters skill | Time-of-day profile baseline; skill against the strongest baseline |
| Pilot agents | One test period decided the verdict, though a single period can be unusual | Rolling-origin backtest over three later blocks |
| Pilot agents | No way to add the agent's own model; no "change from the last value" model | `custom_models` hook; `gbm_change` candidate |
| Pilot agents | No range on forecasts; no view of what the model relies on | 90% prediction intervals with test coverage; grouped input drivers |

**Table A2.** Changes after the reported experiments (not evaluated in Section 6).

| Found by | Problem | Fix |
|---|---|---|
| Pilot agents | The deployed model never trained on the most recent (test) period | `refit_all` option: after evaluation, refit the chosen configuration on all data for deployment, recorded as such |
| Pilot agents | Missing quantities: VOC, sound level, barometric pressure, water flow | Added |
| Pilot agents | Saved forests predicted in parallel threads, so repeated forecasts differed by about 1e-15 | Saved models predict single-threaded and repeat exactly |
| Lifecycle experiment (E4) | Monitoring compared a model only with its own test-time error, so a model worse than persistence (district heating in summer) was never flagged | Drift checks also score the baseline on the same recent rows and recommend falling back to it |
| Case-study re-run (ROBOD Room 3, after the dead-meter mask) | Gradient boosting crashed when an input had no values at all in an early tuning fold | Such inputs are left out of that fit; otherwise identical to the plain estimator (test added) |
| Pilot agents (T2) | A meter reading zero while the equipment it measures is running is not flagged by any single-column check | Not fixed in the package; the case-study loader masks such days, and the skill asks the agent to look for contradictions between related points |

This is principle P9 of Kreuzberger et al. [2023], feedback loops, applied to
the framework itself.

## Appendix B. Evaluation protocol per task

**Table B1.** RMSE of the same random forest on the same rows under each protocol, in the target's own unit. The time-ordered holdout scores a different, later window and is shown for reference.

<!-- table: protocol_tasks -->
