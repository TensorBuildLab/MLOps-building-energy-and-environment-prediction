# S1. Package history {-}

The framework was revised in four rounds: a first version was run on the ROBOD and Aalborg data; an independent agent reviewed the code with instructions only to find correctness problems; the agents of the formative usability study (Section S3) used it; and a mock peer review of an earlier version of this paper led to the baselines and gate changes of version 0.3. Every problem found was fixed with a regression test. Table S1 lists the fixes made before the earlier version of this study (package 0.2.0.dev0); Table S2 lists the changes made since. All of them are in version 0.3.1 (package fingerprint 84f7e16c74ac9fdc), which was frozen before any experiment of this paper was run and produced every result in it.

**Table S1.** Fixes made before the earlier version of the study.

| Found by | Problem | Fix |
|---|---|---|
| Real data (ROBOD) | Stuck-sensor runs and spikes were counted across gaps in the data (weekends missing) | Runs and spike windows never span a gap |
| Real data (ROBOD, Aalborg) | Solar, illuminance, PM2.5 and supply-air temperature were flagged for spikes that are real | Spike checks disabled for those quantities |
| Real data (ROBOD, Aalborg) | No way to state that a sensor's flat stretches are normal (CO2 floor at 400 ppm, change-of-value logging) | *flat_ok* declaration; the stuck warning recognizes change-of-value logging from the share of unchanged steps |
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
| Usability-study agents and code review | Cleaning decisions looked ahead: centred spike windows; stuck stretches masked from their start | Causal cleaning: spikes judged against earlier readings, stuck stretches masked from the moment they are detectable |
| Usability-study agents | Timestamps whose UTC offset changes at daylight saving raised a bare pandas error | *tz=* option; offsets parsed and converted to the building's zone |
| Usability-study agents | A unit switch part-way through a series was reported only as "out of range" | The switch time and the likely unit are reported |
| Usability-study agents | Persistence is a weak reference for scheduled loads, which flatters skill | Time-of-day profile baseline; skill against the strongest baseline |
| Usability-study agents | One test period decided the verdict, though a single period can be unusual | Rolling-origin backtest over three later blocks |
| Usability-study agents | No way to add the agent's own model; no "change from the last value" model | *custom_models* hook; *gbm_change* candidate |
| Usability-study agents | No range on forecasts; no view of what the model relies on | 90% prediction intervals with test coverage; grouped input drivers |

**Table S2.** Changes made after the earlier version of the study, all included in the evaluated version 0.3.1.

| Found by | Problem | Change |
|---|---|---|
| Usability-study agents | The deployed model never trained on the most recent (test) period | *refit_all* option: after evaluation, refit the chosen configuration on all data for deployment, recorded as such |
| Usability-study agents | Missing quantities: VOC, sound level, barometric pressure, water flow | Added (28 quantities) |
| Usability-study agents | Saved forests predicted in parallel threads, so repeated forecasts differed by about 1e-15 | Saved models predict single-threaded and repeat exactly |
| Earlier lifecycle experiment | Monitoring compared a model only with its own test-time error, so a model worse than persistence (district heating in summer) was never flagged | Drift checks also score the baseline on the same recent rows and recommend falling back to it |
| Re-run after the dead-meter mask (ROBOD Room 3) | Gradient boosting crashed when an input had no values at all in an early tuning fold | Such inputs are left out of that fit; otherwise identical to the plain estimator |
| Usability-study agents (T2) | A meter reading zero while the equipment it measures is running is not flagged by any single-column check | Not fixed in the package; the case-study loader masks such days, and the skill asks the agent to look for contradictions between related points |
| Mock review | The reference set lacked the M&V standard and weekly patterns | Same time last week, 168-h time-of-week profile, TOWT regression with CalTRACK knots, time-of-day probability profile for binary targets |
| Mock review | Guideline 14 was a promotion gate for forecasts, which may use lags of the metered target | Gate only for estimation-mode energy models; reported for the model and its reference otherwise |
| Mock review | The length and completeness of the test window were not recorded | Test days and test completeness in every run record; the reference model is kept in the results |
| Smoke test before the experiments | TOWT was numerically unstable when a temperature segment had few training hours (version 0.3.0) | Segments with fewer than 20 training hours are merged (0.3.1) |

# S2. Division of labor and package modules {-}

**Table S3.** Division of labor between the agent and the package.

| The agent (judgment) | The package (checks that are the same for every model) |
|:---|:---|
| Clarify the target, horizon and intended use with the person who asked | Refuse to fit while data errors are unresolved |
| Load any export format | Accept any table with a time index |
| Decode point names; declare quantity and unit | Check every declaration against physical ranges and name the likely unit when it is wrong |
| Decide what faults and unusual periods mean | Detect stuck sensors, spikes, placeholder values, text, duplicates, gaps and cumulative meters |
| Design extra inputs; mark what is known in advance | Shift every measured input by the horizon and audit how far each input reaches |
| Add its own models if needed | Evaluate every model in the same way: in time order, against the strongest no-ML baseline |
| Explain the results | Report, model card, gates, registry, monitoring and one record per run |

**Table S4.** Modules of the bemlops package (version 0.3.1).

| Module | Role |
|---|---|
| *quantities*, *schema* | 28 physical quantities with units, conversions, plausible and typical ranges, and flags; parsing of declarations |
| *cleaning*, *checks* | Causal detectors for export and sensor problems; the data report with blocking errors |
| *prepare* | Logged standard preparation and resampling |
| *features*, *split* | Inputs shifted by the horizon, with an audit; time-ordered splits with a gap |
| *models*, *metrics* | Baselines (persistence, same time yesterday and last week, time-of-day and time-of-week profiles, TOWT, mean, share of ones, time-of-day probability) and tuned candidates; RMSE, MAE, CV(RMSE), NMBE, Guideline 14, Brier score, accuracy, balanced accuracy, F1, ROC AUC |
| *project* | The workflow, its configuration, backtest, intervals and input drivers |
| *report*, *governance* | Run record, report, model card; promotion gates |
| *deploy*, *registry*, *pipeline*, *cli* | Deployable model with live validation and drift checks; registry with stages, champion/challenger and rollback; scheduled pipelines; command line |

# S3. Formative usability study with independent agents {-}

## Design {-}

To separate the framework from the agent that built it, fresh agent instances were each given a folder that contained only a raw export with planted faults and a task description. Each agent had to deliver a *predict* function and a report stating the RMSE it expected on future data. Task T1 was CO~2~ in Aalborg Room B 1 h ahead, with training data up to May 2023 and June hidden; task T2 was chilled-water energy in ROBOD Room 5 1 h ahead, with the last fifth of the days hidden. In the agent-alone arm the agent had pandas and scikit-learn only, and bemlops was forbidden; in the framework arm the agent was told to follow the Agent Skill. Each arm ran with Claude Opus 5.5 and Claude Sonnet 5.5, giving eight runs. The agents could not see the hidden data or the evaluation code, and their launch prompts are published with the code. Each deliverable was scored on whether it ran; its RMSE on the hidden period against the clean target, as skill against persistence and against the time-of-day profile computed without the dead-meter days; an automatic leakage test that perturbs every value at or after $T$ − 45 min for 15 random hidden-period times $T$ and checks that the forecast for $T$ is unchanged; and the ratio of the achieved to the self-reported RMSE. The code and reports were also audited by hand, and the tokens, tool calls and wall-clock time of each run were recorded. The framework arm used an earlier package version (git commit 5c575a6) than the experiments of the paper. With one run per cell, the study is formative: it asks whether the effects the framework is designed for appear at all with agents that did not write it, and it found defects that were then fixed (Table S1).

## Results {-}

All eight deliverables ran on the hidden data and passed the leakage test: no forecast changed when every later value was perturbed (Table S5). For T1 (Room B CO~2~, June hidden), no agent beat persistence by a meaningful margin, with skills from −0.04 to 0.06. June was quiet: the persistence RMSE was 21 ppm, against 29–48 ppm in the spring blocks on which the agents had validated. Against the time-of-day profile, every agent had a skill of 0.71–0.73, because CO~2~ depends more on who is in the room than on the hour. For T2 (chilled-water energy), all agents reached a skill of 0.75–0.76 against persistence and 0.16–0.21 against the time-of-day profile, the stronger baseline for this scheduled load. That profile was computed from the training period without the dead-meter days; with those days included, the profile is much weaker and the skill would have appeared to be 0.65–0.67.

**Table S5.** Usability-study results on the hidden periods.

<!-- table: j_pilot -->

Within each task and model, the framework made no consistent difference to accuracy. For T1 with Opus, the framework run was better by 1.45 ppm (95% day-block bootstrap interval −2.50 to −0.32 ppm), whereas for T1 with Sonnet it was worse by 1.80 ppm (0.80 to 2.80 ppm); for T2 both differences were within 0.04 kWh, and both intervals included zero. With one run per cell, these signs reflect run-to-run variation as much as the arm. Every agent overestimated its own error, with ratios of achieved to self-reported RMSE of 0.59–0.82.

Table S6 summarizes the manual audit. The agents found 7 or 8 of the 8 planted faults with or without the framework (29 of 32 with it and 30 of 32 without), and all T1 agents missed the three-day stuck ventilation meter, an input that none of them used. Every T2 agent found the dead chilled-water meter, which had not been planted, as well as catch-up readings after communication losses; the framework's checks flagged neither. Seven of the eight agents wrote their own test that forecasts do not use later data, including all four framework agents, although the framework already audits its own inputs.

**Table S6.** What each agent found and built, and what it cost (manual audit of code and reports; usage counters of the agent runs).

<!-- table: j_pilot_audit -->

Two of the four framework agents, both Sonnet, used its checks but replaced its model with their own; one of them turned off the framework's masking, judging it to look ahead, which it did in that earlier version. The other two, both Opus, kept a framework model but had to adapt it: the T1 agent made it predict the change from the latest value and moved the split so that training covered a new ventilation schedule, and the T2 agent added its own schedule and holiday inputs. All four gave the same reasons: they could not add their own inputs or models, there was no model of the change from the latest value, there was only one test window, and persistence was the only reference for a scheduled load. The framework arm used more tokens than the agent-alone arm in all four pairs (5–52% more) and more tool calls in all four (32–89% more), and took longer in three of the four. How much of this came from the usability report that only the framework arm was asked for, from reading the skill, or from working around the defects of the earlier version cannot be separated.

## Limits {-}

The study has one run per cell, two tasks and two models from one provider, and the agents were capable enough to find almost every planted fault on their own; it cannot show whether the framework helps less careful agents or analysts, which is the use it is designed for. Its framework arm used a version with defects that were fixed afterwards, partly because of what the agents reported. The launch prompts, the delivered code and reports (without data or model binaries), the manual audit and the hidden-period scores are in the benchmarks/pilot folder of the repository; the task descriptions are generated by benchmarks/pilot/make_tasks.py, and the deliverables can be re-scored with benchmarks/pilot/score.py.

# S4. Evaluation protocol per task {-}

**Table S7.** RMSE of the same random forest on the same rows under each protocol, in the unit of each target (kWh for BDG2). "Folds 2–5": the rows on which forward chaining can be evaluated.

<!-- table: s_protocol_v3 -->

# S5. Aalborg lifecycle case {-}

**Table S8.** Mean monthly RMSE of each policy from May to December 2023 (kW for district heating, ppm for CO~2~).

<!-- table: v3_lifecycle_aalborg -->

**Table S9.** District-heating power 1 h ahead: monthly RMSE (kW) of each policy, May–December 2023. "(P)": months in which the fallback serves persistence. Drift ratio: recent error divided by the error at test time.

<!-- table: s_lifecycle_aalborg_dh -->

**Table S10.** Room A CO~2~ 1 h ahead: monthly RMSE (ppm) of each policy, as in Table S9.

<!-- table: s_lifecycle_aalborg_co2 -->

# S6. Data issues on the untouched data {-}

**Table S11.** Distinct warnings and errors raised by the data check on the untouched data, by type and dataset. An issue counts once per column and data source (a BDG2 meter or site weather station, a ROBOD room, the Aalborg export), however many tasks used the column.

<!-- table: v3_issue_types -->

# S7. Results of every task {-}

**Table S12.** Chosen model, reference baseline, test skill with its day-block bootstrap interval, DM result, backtest skill, coverage of the 90% interval, test days and gate decision for each of the 272 tasks. Skill is defined on RMSE (Brier score for binary targets) against the reference baseline; a chosen baseline has skill 0 by definition.

<!-- table: s_all_tasks_v3 -->

# S8. Gate sensitivity and protocol verdicts {-}

**Table S13.** Number of tasks with a promoted model under the evaluated gates and stricter variants (all other gates unchanged), out of 272 tasks.

<!-- table: v3_gates -->

**Table S14.** Hourly Guideline 14 verdicts of the day-ahead models of 40 BDG2 buildings under each protocol, on the same rows (blocked folds 2–5).

<!-- table: v3_protocol_g14 -->
