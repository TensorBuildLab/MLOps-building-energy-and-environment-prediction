# Run report: bdg2-Wolf_education_Vivian

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3 for 14 h (2016-11-02 19:00:00 to 2016-11-03 09:00:00); 51 such stretch(es), 14 d 10 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `windSpeed`: 51 stuck stretch(es) set to missing. (90)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (20)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (20)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (70)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 14:00:00 | 12278 |
| val | 2017-05-27 15:00:00 | 2017-09-13 06:00:00 | 2607 |
| test | 2017-09-14 07:00:00 | 2017-12-31 23:00:00 | 2608 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 23.803 | 15.377 | 35.899 | 1.525 | 0.428 |
| gbm_change | ml | 23.813 | 15.269 | 35.914 | 1.215 | 0.427 |
| ridge | ml | 25.563 | 18.229 | 38.552 | -1.449 | 0.340 |
| towt | baseline | 26.646 | 17.233 | 40.185 | -2.317 | 0.283 |
| time_of_day_profile | baseline | 27.037 | 18.290 | 40.776 | -8.301 | 0.261 |
| time_of_week_profile | baseline | 27.234 | 18.360 | 41.073 | -8.292 | 0.251 |
| same_time_yesterday | baseline | 32.321 | 20.042 | 48.745 | 0.278 | -0.055 |
| persistence | baseline | 32.321 | 20.042 | 48.745 | 0.278 | -0.055 |
| same_time_last_week | baseline | 35.059 | 22.344 | 52.873 | 0.493 | -0.242 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 20.997 | 24.476 |
| MAE (kWh) | 14.364 | 17.084 |
| CV(RMSE) % | 28.575 | 33.310 |
| NMBE % | -0.126 | 1.711 |
| R² | 0.662 | 0.541 |

Skill vs towt: **0.14** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 28.6% (limit 30%), NMBE -0.1% (limit ±10%): **passes**.

90% prediction interval: ±39.2 kWh (width from validation errors); it contained 92% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.11 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.08 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.19 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 77% |
| electricity (recent history) | 22% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
