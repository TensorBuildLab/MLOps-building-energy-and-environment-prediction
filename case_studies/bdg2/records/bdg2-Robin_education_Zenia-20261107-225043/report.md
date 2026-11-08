# Run report: bdg2-Robin_education_Zenia

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 142.272 for 43 d 10 h (2016-03-08 13:00:00 to 2016-04-20 23:00:00); 5 such stretch(es), 70 d 15 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 5 stuck stretch(es) set to missing. (1670)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-16 12:00:00 | 11111 |
| val | 2017-06-17 13:00:00 | 2017-09-23 17:00:00 | 2357 |
| test | 2017-09-24 18:00:00 | 2017-12-31 23:00:00 | 2358 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 14.832 | 10.539 | 5.946 | 0.327 | 0.921 |
| gbm | ml | 19.034 | 12.347 | 7.631 | 0.173 | 0.870 |
| ridge | ml | 20.473 | 14.707 | 8.208 | -1.588 | 0.849 |
| same_time_last_week | baseline | 24.798 | 17.406 | 9.941 | -0.997 | 0.779 |
| same_time_yesterday | baseline | 36.021 | 20.269 | 14.441 | -0.240 | 0.533 |
| persistence | baseline | 36.021 | 20.269 | 14.441 | -0.240 | 0.533 |
| time_of_week_profile | baseline | 62.044 | 54.088 | 24.873 | 21.688 | -0.384 |
| time_of_day_profile | baseline | 62.084 | 54.133 | 24.889 | 21.706 | -0.386 |
| towt | baseline | 65.409 | 57.865 | 26.222 | 23.201 | -0.538 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 9.118 | 14.566 |
| MAE (kWh) | 6.734 | 9.529 |
| CV(RMSE) % | 4.239 | 6.772 |
| NMBE % | -0.206 | -1.535 |
| R² | 0.947 | 0.864 |

Skill vs same_time_last_week: **0.37** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 4.2% (limit 30%), NMBE -0.2% (limit ±10%): **passes**.

90% prediction interval: ±23.8 kWh (width from validation errors); it contained 98% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-16 to 2017-08-21 | 1588 | 0.43 |
| 2017-08-21 to 2017-10-26 | 1588 | 0.21 |
| 2017-10-26 to 2017-12-31 | 1587 | 0.44 |

Pooled skill: **0.39**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 65% |
| calendar (time of day, weekday) | 35% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
