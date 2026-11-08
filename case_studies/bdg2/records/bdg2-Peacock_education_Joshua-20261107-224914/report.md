# Run report: bdg2-Peacock_education_Joshua

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 17 h (2016-01-08 15:00:00 to 2016-01-09 08:00:00); 48 such stretch(es), 14 d 14 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 48 stuck stretch(es) set to missing. (110)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (58)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (11)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (65)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-27 19:00:00 | 12215 |
| val | 2017-05-28 20:00:00 | 2017-09-13 20:00:00 | 2593 |
| test | 2017-09-14 21:00:00 | 2017-12-31 23:00:00 | 2595 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 15.856 | 10.870 | 3.470 | -0.126 | 0.769 |
| gbm | ml | 15.916 | 11.119 | 3.483 | -0.238 | 0.768 |
| towt | baseline | 17.207 | 12.254 | 3.766 | -0.363 | 0.729 |
| ridge | ml | 17.532 | 12.672 | 3.837 | 0.432 | 0.718 |
| time_of_week_profile | baseline | 19.576 | 14.043 | 4.284 | -2.009 | 0.649 |
| time_of_day_profile | baseline | 20.503 | 14.308 | 4.487 | -2.013 | 0.615 |
| same_time_last_week | baseline | 20.767 | 14.909 | 4.545 | 0.206 | 0.605 |
| persistence | baseline | 30.311 | 19.452 | 6.634 | 0.124 | 0.158 |
| same_time_yesterday | baseline | 30.311 | 19.452 | 6.634 | 0.124 | 0.158 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 14.998 | 18.555 |
| MAE (kWh) | 10.838 | 13.518 |
| CV(RMSE) % | 3.203 | 3.963 |
| NMBE % | 0.841 | 0.273 |
| R² | 0.768 | 0.645 |

Skill vs towt: **0.19** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 3.2% (limit 30%), NMBE 0.8% (limit ±10%): **passes**.

90% prediction interval: ±23.3 kWh (width from validation errors); it contained 90% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-08 | 1746 | 0.09 |
| 2017-08-08 to 2017-10-20 | 1745 | -0.01 |
| 2017-10-20 to 2017-12-31 | 1745 | 0.25 |

Pooled skill: **0.14**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 62% |
| calendar (time of day, weekday) | 37% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
