# Run report: bdg2-Robin_education_Kristopher

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 12280 |
| val | 2017-05-27 16:00:00 | 2017-09-13 06:00:00 | 2607 |
| test | 2017-09-14 07:00:00 | 2017-12-31 23:00:00 | 2609 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 35.048 | 25.083 | 26.180 | 1.644 | 0.329 |
| gbm | ml | 36.555 | 26.455 | 27.305 | 2.123 | 0.270 |
| ridge | ml | 37.321 | 25.988 | 27.877 | 2.169 | 0.239 |
| towt | baseline | 39.877 | 33.230 | 29.787 | 9.678 | 0.131 |
| time_of_day_profile | baseline | 40.046 | 32.981 | 29.913 | 9.493 | 0.123 |
| time_of_week_profile | baseline | 40.127 | 33.008 | 29.974 | 9.481 | 0.120 |
| same_time_yesterday | baseline | 43.668 | 28.115 | 32.619 | 0.463 | -0.042 |
| persistence | baseline | 43.668 | 28.115 | 32.619 | 0.463 | -0.042 |
| same_time_last_week | baseline | 52.362 | 40.148 | 39.113 | 1.748 | -0.499 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 12.967 | 16.675 |
| MAE (kWh) | 8.702 | 11.460 |
| CV(RMSE) % | 9.962 | 12.811 |
| NMBE % | 0.447 | 6.370 |
| R² | 0.689 | 0.485 |

Skill vs towt: **0.22** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 10.0% (limit 30%), NMBE 0.4% (limit ±10%): **passes**.

90% prediction interval: ±56.8 kWh (width from validation errors); it contained 100% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.16 |
| 2017-08-07 to 2017-10-19 | 1755 | 0.10 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.25 |

Pooled skill: **0.15**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 68% |
| calendar (time of day, weekday) | 32% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
