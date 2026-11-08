# Run report: bdg2-Bull_education_Brady

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 18 for 10 h (2017-12-25 22:00:00 to 2017-12-26 08:00:00); 15 such stretch(es), 4 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 15 stuck stretch(es) set to missing. (27)
- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-26 10:00:00 | 12051 |
| val | 2017-05-27 11:00:00 | 2017-09-11 09:00:00 | 2558 |
| test | 2017-09-12 10:00:00 | 2017-12-31 23:00:00 | 2559 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 3.968 | 2.575 | 13.634 | -2.943 | 0.869 |
| gbm_change | ml | 4.065 | 2.678 | 13.966 | -1.991 | 0.862 |
| ridge | ml | 4.461 | 3.289 | 15.329 | -0.237 | 0.834 |
| same_time_last_week | baseline | 4.608 | 2.952 | 15.834 | 0.779 | 0.823 |
| towt | baseline | 6.795 | 4.752 | 23.346 | -13.215 | 0.616 |
| time_of_week_profile | baseline | 7.814 | 5.730 | 26.849 | -18.397 | 0.491 |
| time_of_day_profile | baseline | 7.842 | 5.823 | 26.944 | -18.422 | 0.488 |
| persistence | baseline | 8.064 | 4.916 | 27.709 | -0.192 | 0.458 |
| same_time_yesterday | baseline | 8.064 | 4.916 | 27.709 | -0.192 | 0.458 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 4.964 | 8.146 |
| MAE (kWh) | 2.863 | 4.453 |
| CV(RMSE) % | 14.775 | 24.246 |
| NMBE % | -1.945 | -3.707 |
| R² | 0.906 | 0.747 |

Skill vs same_time_last_week: **0.39** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.8% (limit 30%), NMBE -1.9% (limit ±10%): **passes**.

90% prediction interval: ±5.44 kWh (width from validation errors); it contained 88% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-06 | 1722 | 0.16 |
| 2017-08-06 to 2017-10-17 | 1722 | 0.25 |
| 2017-10-17 to 2017-12-31 | 1721 | 0.41 |

Pooled skill: **0.34**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 71% |
| calendar (time of day, weekday) | 29% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
