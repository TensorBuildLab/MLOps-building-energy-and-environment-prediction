### 6.7 What the evaluation changed in the framework

The framework was revised twice during this study. A first version was run
on the real datasets. It was then reviewed by an independent agent that read
the code with no other instructions than to find correctness problems, and
used by the pilot agents of E5. Every problem found was fixed with a
regression test before the final runs reported here (Table 9). Most problems
were invisible on synthetic data.

**Table 9.** Problems found by the evaluation and how they were fixed.

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

This is principle P9 of Kreuzberger et al. [2023], feedback loops, applied to
the framework itself. The agents that used the framework were also its most
useful testers.
