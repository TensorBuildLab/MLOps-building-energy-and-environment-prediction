# Run report: bdg2-Eagle_education_Brooke

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 851.375 for 3 d 9 h (2017-12-28 07:00:00 to 2017-12-31 16:00:00); 24 such stretch(es), 29 d 15 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 24 stuck stretch(es) set to missing. (591)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-29 13:00:00 | 11840 |
| val | 2017-05-30 14:00:00 | 2017-09-12 21:00:00 | 2513 |
| test | 2017-09-13 22:00:00 | 2017-12-31 17:00:00 | 2514 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| towt | baseline | 27.602 | 17.085 | 3.114 | -0.478 | 0.661 |
| ridge | ml | 30.746 | 20.584 | 3.469 | 0.514 | 0.579 |
| same_time_last_week | baseline | 37.150 | 21.580 | 4.192 | 0.113 | 0.385 |
| time_of_day_profile | baseline | 40.375 | 31.338 | 4.555 | -3.348 | 0.274 |
| time_of_week_profile | baseline | 40.515 | 31.578 | 4.571 | -3.349 | 0.269 |
| same_time_yesterday | baseline | 43.897 | 27.667 | 4.953 | -0.014 | 0.142 |
| persistence | baseline | 43.897 | 27.667 | 4.953 | -0.014 | 0.142 |
| gbm | ml | 55.444 | 38.778 | 6.256 | 0.964 | -0.369 |
| gbm_change | ml | 65.553 | 36.306 | 7.396 | 1.489 | -0.914 |

## Test result

Chosen model: **towt** 

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 43.067 | 43.067 |
| MAE (kWh) | 29.004 | 29.004 |
| CV(RMSE) % | 4.790 | 4.790 |
| NMBE % | -1.729 | -1.729 |
| R² | 0.377 | 0.377 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 4.8% (limit 30%), NMBE -1.7% (limit ±10%): **passes**.

90% prediction interval: ±33.8 kWh (width from validation errors); it contained 69% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-29 to 2017-08-08 | 1692 | 0.00 |
| 2017-08-08 to 2017-10-18 | 1692 | 0.00 |
| 2017-10-18 to 2017-12-31 | 1691 | 0.00 |

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
