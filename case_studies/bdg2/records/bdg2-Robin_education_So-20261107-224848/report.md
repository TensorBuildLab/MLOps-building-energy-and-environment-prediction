# Run report: bdg2-Robin_education_So

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 476.329 for 43 d 10 h (2016-03-08 13:00:00 to 2016-04-20 23:00:00); 9 such stretch(es), 74 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 9 stuck stretch(es) set to missing. (1738)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-17 09:00:00 | 11064 |
| val | 2017-06-18 10:00:00 | 2017-09-24 03:00:00 | 2346 |
| test | 2017-09-25 04:00:00 | 2017-12-31 23:00:00 | 2348 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 14.634 | 10.443 | 2.980 | 0.359 | 0.930 |
| gbm_change | ml | 14.905 | 10.276 | 3.035 | 0.127 | 0.927 |
| ridge | ml | 18.404 | 14.242 | 3.747 | -0.385 | 0.889 |
| same_time_last_week | baseline | 19.638 | 14.737 | 3.998 | -0.356 | 0.873 |
| time_of_week_profile | baseline | 20.108 | 15.468 | 4.094 | -0.601 | 0.867 |
| time_of_day_profile | baseline | 20.590 | 15.870 | 4.192 | -0.589 | 0.861 |
| towt | baseline | 21.587 | 16.841 | 4.395 | 1.167 | 0.847 |
| persistence | baseline | 36.405 | 21.164 | 7.412 | -0.055 | 0.564 |
| same_time_yesterday | baseline | 36.405 | 21.164 | 7.412 | -0.055 | 0.564 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 15.084 | 32.639 |
| MAE (kWh) | 10.795 | 20.131 |
| CV(RMSE) % | 3.088 | 6.683 |
| NMBE % | -0.481 | -1.569 |
| R² | 0.960 | 0.811 |

Skill vs same_time_last_week: **0.54** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 3.1% (limit 30%), NMBE -0.5% (limit ±10%): **passes**.

90% prediction interval: ±22.9 kWh (width from validation errors); it contained 90% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-17 to 2017-08-22 | 1581 | 0.28 |
| 2017-08-22 to 2017-10-27 | 1581 | 0.24 |
| 2017-10-27 to 2017-12-31 | 1580 | 0.58 |

Pooled skill: **0.45**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 74% |
| calendar (time of day, weekday) | 26% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
