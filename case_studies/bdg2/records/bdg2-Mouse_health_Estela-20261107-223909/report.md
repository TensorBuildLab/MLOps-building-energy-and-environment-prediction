# Run report: bdg2-Mouse_health_Estela

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 395.205 for 8 d 22 h (2016-01-06 01:00:00 to 2016-01-14 23:00:00); 23 such stretch(es), 49 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 23 stuck stretch(es) set to missing. (1069)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-04-12 03:00:00 | 10371 |
| val | 2017-04-13 04:00:00 | 2017-07-23 06:00:00 | 2198 |
| test | 2017-07-24 07:00:00 | 2017-10-23 23:00:00 | 2200 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| towt | baseline | 32.324 | 18.972 | 8.377 | -0.791 | 0.897 |
| time_of_week_profile | baseline | 34.613 | 21.745 | 8.970 | -0.630 | 0.882 |
| gbm | ml | 35.933 | 21.801 | 9.312 | 0.243 | 0.873 |
| time_of_day_profile | baseline | 36.215 | 23.115 | 9.385 | -0.583 | 0.871 |
| gbm_change | ml | 45.691 | 27.219 | 11.841 | 0.734 | 0.795 |
| ridge | ml | 47.629 | 33.343 | 12.343 | 0.418 | 0.777 |
| same_time_last_week | baseline | 60.671 | 39.502 | 15.723 | 0.775 | 0.639 |
| persistence | baseline | 71.668 | 43.366 | 18.573 | 0.005 | 0.496 |
| same_time_yesterday | baseline | 71.668 | 43.366 | 18.573 | 0.005 | 0.496 |

## Test result

Chosen model: **towt** 

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 32.985 | 32.985 |
| MAE (kWh) | 20.270 | 20.270 |
| CV(RMSE) % | 9.032 | 9.032 |
| NMBE % | -5.009 | -5.009 |
| R² | 0.882 | 0.882 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 9.0% (limit 30%), NMBE -5.0% (limit ±10%): **passes**.

90% prediction interval: ±36.9 kWh (width from validation errors); it contained 93% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-04-12 to 2017-06-21 | 1482 | 0.00 |
| 2017-06-21 to 2017-08-23 | 1482 | 0.00 |
| 2017-08-23 to 2017-10-23 | 1482 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| airTemperature | 100% |

> Warning: No machine-learning model beat the 'towt' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
