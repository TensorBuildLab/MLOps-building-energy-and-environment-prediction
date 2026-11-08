# Run report: bdg2-Robin_lodging_Armand

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 39.841 for 43 d 10 h (2016-03-08 13:00:00 to 2016-04-20 23:00:00); 21 such stretch(es), 79 d 11 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 21 stuck stretch(es) set to missing. (1802)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-18 04:00:00 | 11019 |
| val | 2017-06-19 05:00:00 | 2017-09-24 13:00:00 | 2337 |
| test | 2017-09-25 14:00:00 | 2017-12-31 23:00:00 | 2338 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 1.716 | 1.166 | 6.069 | -0.874 | 0.790 |
| persistence | baseline | 1.810 | 1.158 | 6.401 | 0.317 | 0.766 |
| same_time_yesterday | baseline | 1.810 | 1.158 | 6.401 | 0.317 | 0.766 |
| ridge | ml | 1.972 | 1.435 | 6.977 | 0.535 | 0.722 |
| gbm | ml | 1.975 | 1.490 | 6.985 | -2.294 | 0.722 |
| same_time_last_week | baseline | 3.111 | 2.090 | 11.004 | -0.032 | 0.309 |
| towt | baseline | 9.765 | 8.294 | 34.538 | -28.365 | -5.805 |
| time_of_day_profile | baseline | 12.238 | 11.103 | 43.287 | -39.156 | -9.689 |
| time_of_week_profile | baseline | 12.245 | 11.108 | 43.310 | -39.148 | -9.700 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 2.875 | 3.226 |
| MAE (kWh) | 2.108 | 2.366 |
| CV(RMSE) % | 6.731 | 7.553 |
| NMBE % | 0.846 | -0.193 |
| R² | 0.911 | 0.888 |

Skill vs persistence: **0.11** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 6.7% (limit 30%), NMBE 0.8% (limit ±10%): **passes**.

90% prediction interval: ±2.51 kWh (width from validation errors); it contained 69% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-18 to 2017-08-22 | 1575 | 0.04 |
| 2017-08-22 to 2017-10-27 | 1574 | 0.16 |
| 2017-10-27 to 2017-12-31 | 1574 | 0.07 |

Pooled skill: **0.09**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 93% |
| calendar (time of day, weekday) | 7% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
