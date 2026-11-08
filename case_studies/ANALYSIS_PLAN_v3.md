# Pre-specified analysis plan, revision v3 (2026-11-07)

Written and committed before any v3 result was computed, in response to a mock review for Applied Energy.
Every v3 experiment runs on one frozen package version, bemlops 0.3.1; each run record carries its
package fingerprint. Earlier (v2) results stay in the repository as `results_v2/` and `records_v2/`.

## Amendment (2026-11-07, before any v3 result was used)
A smoke test of the M&V script showed that the TOWT baseline of 0.3.0 was numerically unstable when a
temperature segment had few training hours (one cross-validation fold produced errors of about 400 kWh).
The first E1 launch on 0.3.0 was stopped and its runs discarded. 0.3.1 merges sparse temperature segments
(at least 20 training hours per segment, as CalTRACK merges sparse bins); everything below runs on 0.3.1.

## Package changes in 0.3.0/0.3.1 (before any run)
- Extra no-ML baselines, all chosen among on validation like the existing ones: same time last week
  (forecasts); a 168-hour time-of-week profile; a time-of-week-and-temperature (TOWT) regression with fixed
  CalTRACK knots, using the temperature available at prediction time (lagged by the horizon for forecasts,
  concurrent for estimates); a time-of-day probability profile for yes/no targets.
- The Guideline 14 hourly criteria are computed for the model and for its reference baseline; they are a
  promotion gate only for estimation-mode (M&V) models and are reported, not gated, for forecasts.
- Each run records the number of test days and the completeness of the test window.

## Samples
- ROBOD: 5 rooms x 9 targets (45 tasks), as in v2, with the dead-meter days masked.
- Aalborg: 27 tasks, as in v2.
- BDG2: buildings with >= 90% of hourly electricity present in the dataset's cleaned meters
  (`electricity_cleaned.csv`), at sites with weather data; sampled round-robin over sites after a random
  shuffle with seed 0; the first **200** in that order (the first 20 are the v2 sample). This is fixed
  before results. The first **40** of the 200 are used for the protocol experiment and the first **50** with
  >= 90% coverage in each of 2016 and 2017 for the lifecycle experiment.

## Experiments and primary outcomes
- **E1 (all tasks, v3 baselines).** Skill against the strongest baseline on validation; Diebold–Mariano test
  (two-sided, HAC with Bartlett kernel, lag = max(h, Newey–West)); day-block bootstrap interval for skill;
  test days; gate decisions. Proportions reported per dataset group (development: ROBOD, Aalborg;
  near-held-out: BDG2) with cluster-bootstrap intervals over rooms/buildings (2,000 resamples).
  Sensitivity: gates with a significant DM result required; a minimum of 7 test days; backtest and test both
  positive; skill threshold 0, 0.05, 0.10.
- **E2 (protocol; 22 room tasks + 40 BDG2 buildings).** Same random forest and rows: shuffled 5-fold CV;
  shuffled CV with univariate feature selection on all rows; shuffled CV with the same selection inside each
  training fold; blocked 5-fold CV with a buffer; forward chaining (test blocks = blocked folds 2–5, training
  on earlier data only, minus the buffer). Primary: RMSE ratio blocked/shuffled and forward/shuffled on
  identical rows (folds 2–5). BDG2: hourly CV(RMSE) and NMBE under each protocol, and the Guideline 14
  verdict each protocol would give.
- **E3 (planted faults; Aalborg Room A, 10 seeds).** v2 arms plus: quick script on clean data; a competent
  script that also drops sentinel values (-999, 9999, 32767) and physically impossible readings and does not
  fill across gaps longer than 1 h. Primary: MAE and RMSE against the clean target; paired Wilcoxon tests.
  False alarms: issues raised on the untouched data of all datasets per series-month; issue subtypes shown.
- **E4 (lifecycle; Aalborg 2 series as before + 50 BDG2 buildings).** BDG2: day-ahead hourly electricity,
  initial training on 2016, deployment January–December 2017; one model fitted per month on all earlier data
  (same settings). Arms: static, monthly, quarterly, drift-triggered with tolerance 1.1, 1.25, 1.5, 2.0
  (error ratio or > 20% of an input outside its training range), gated (drift-triggered at 1.5 plus gates and
  champion–challenger on unseen rows), gated with persistence fallback, persistence. Primary: mean monthly
  RMSE and pooled RMSE per building; paired differences between arms with building-level bootstrap intervals.
  **Gate audit:** for every monthly model, its gate decision against its realized skill versus its own
  reference baseline over the following 3 months; false-promotion (promoted, realized skill < 0) and
  false-refusal (refused, realized skill >= threshold) rates for skill thresholds 0, 0.05 and 0.10.
- **E5 (M&V pseudo-savings; the 200 BDG2 buildings with >= 90% coverage in both years).** Baseline period
  2016, reporting period 2017, no measure installed. The framework in estimation mode (h = 0, concurrent
  weather and calendar, no target lags; the chosen configuration refitted on all of 2016) against TOWT fitted
  on all of 2016. Primary: normalized annual pseudo-savings error (sum of predicted minus sum of metered,
  divided by sum of metered) and hourly CV(RMSE) and NMBE in 2017. Protocol link: TOWT's baseline-period
  CV(RMSE) estimated in-sample, by shuffled CV, by blocked CV and by the time-ordered split, against the
  realized 2017 CV(RMSE); share of buildings for which each estimate gives a Guideline 14 verdict that the
  reporting year contradicts. Non-routine screen: buildings whose 2017 mean differs from the 2016 mean by more
  than 30% are flagged; results are reported with and without them.
- **E6 (formative usability study; unchanged, Supplementary Material).** The eight pilot runs, reported as a
  case study with all its limits; no research question rests on it.

## What would change the conclusions
Any headline number is reported as computed under this plan, whether it rises or falls relative to v2.
