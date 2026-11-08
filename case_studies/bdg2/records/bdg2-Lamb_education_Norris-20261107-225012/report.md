# Run report: bdg2-Lamb_education_Norris

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 2.0003 for 14 h (2017-08-22 07:00:00 to 2017-08-22 21:00:00); 14 such stretch(es), 4 d 15 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10 for 1 d 18 h (2017-12-20 15:00:00 to 2017-12-22 09:00:00); 278 such stretch(es), 101 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3.1 for 7 h (2017-09-15 23:00:00 to 2017-09-16 06:00:00); 4 such stretch(es), 1 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 3 single-sample spike(s), e.g. 16, 12.9, 11.8 at 2016-03-28 04:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 14 stuck stretch(es) set to missing. (41)
- mask_stuck `airTemperature`: 278 stuck stretch(es) set to missing. (1035)
- mask_stuck `windSpeed`: 4 stuck stretch(es) set to missing. (5)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (299)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (24)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (31)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-04-26 22:00:00 | 11498 |
| val | 2017-04-27 23:00:00 | 2017-09-20 01:00:00 | 2440 |
| test | 2017-09-21 02:00:00 | 2017-12-31 23:00:00 | 2441 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 3.406 | 2.212 | 47.861 | -16.221 | 0.817 |
| gbm_change | ml | 3.481 | 2.038 | 48.915 | -12.381 | 0.809 |
| ridge | ml | 4.456 | 3.126 | 62.617 | -6.354 | 0.687 |
| same_time_last_week | baseline | 5.276 | 2.579 | 74.145 | -4.015 | 0.562 |
| same_time_yesterday | baseline | 5.851 | 2.516 | 82.230 | -2.382 | 0.461 |
| persistence | baseline | 5.851 | 2.516 | 82.230 | -2.382 | 0.461 |
| towt | baseline | 7.475 | 4.679 | 105.046 | -35.857 | 0.120 |
| time_of_day_profile | baseline | 8.091 | 4.935 | 113.712 | -54.749 | -0.031 |
| time_of_week_profile | baseline | 8.103 | 4.926 | 113.879 | -54.754 | -0.034 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 2.853 | 4.142 |
| MAE (kWh) | 2.025 | 1.922 |
| CV(RMSE) % | 44.541 | 64.674 |
| NMBE % | -17.231 | -7.412 |
| R² | 0.809 | 0.597 |

Skill vs same_time_last_week: **0.31** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 44.5% (limit 30%), NMBE -17.2% (limit ±10%): **does not pass**.

90% prediction interval: ±4.48 kWh (width from validation errors); it contained 90% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-04-26 to 2017-08-15 | 1643 | 0.47 |
| 2017-08-15 to 2017-10-24 | 1643 | 0.03 |
| 2017-10-24 to 2017-12-31 | 1643 | 0.37 |

Pooled skill: **0.38**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 61% |
| calendar (time of day, weekday) | 38% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
