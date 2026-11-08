# Run report: bdg2-Bull_office_Debbie

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 25 for 9 h (2016-12-11 10:00:00 to 2016-12-11 19:00:00); 28 such stretch(es), 7 d 14 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 28 stuck stretch(es) set to missing. (42)
- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-27 08:00:00 | 12004 |
| val | 2017-05-28 09:00:00 | 2017-09-11 22:00:00 | 2548 |
| test | 2017-09-12 23:00:00 | 2017-12-31 23:00:00 | 2549 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 3.364 | 2.086 | 11.916 | -1.127 | 0.863 |
| gbm_change | ml | 3.420 | 2.074 | 12.112 | -0.614 | 0.858 |
| ridge | ml | 3.772 | 2.468 | 13.359 | 0.048 | 0.827 |
| same_time_last_week | baseline | 4.141 | 2.358 | 14.666 | 1.047 | 0.792 |
| time_of_day_profile | baseline | 4.678 | 3.129 | 16.568 | -4.522 | 0.735 |
| time_of_week_profile | baseline | 4.708 | 3.126 | 16.676 | -4.526 | 0.731 |
| towt | baseline | 4.747 | 3.152 | 16.815 | -4.607 | 0.727 |
| persistence | baseline | 6.585 | 3.617 | 23.323 | 0.438 | 0.474 |
| same_time_yesterday | baseline | 6.585 | 3.617 | 23.323 | 0.438 | 0.474 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 4.298 | 7.025 |
| MAE (kWh) | 2.442 | 3.585 |
| CV(RMSE) % | 13.901 | 22.722 |
| NMBE % | 1.418 | -2.773 |
| R² | 0.885 | 0.691 |

Skill vs same_time_last_week: **0.39** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 13.9% (limit 30%), NMBE 1.4% (limit ±10%): **passes**.

90% prediction interval: ±4.26 kWh (width from validation errors); it contained 85% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-06 | 1715 | 0.13 |
| 2017-08-07 to 2017-10-17 | 1715 | 0.20 |
| 2017-10-17 to 2017-12-31 | 1715 | 0.42 |

Pooled skill: **0.34**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 58% |
| calendar (time of day, weekday) | 42% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
