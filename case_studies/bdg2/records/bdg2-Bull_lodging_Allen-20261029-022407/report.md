# Run report: bdg2-Bull_lodging_Allen

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 3.12 for 8 h (2016-12-15 21:00:00 to 2016-12-16 05:00:00); 2 such stretch(es), 14 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 2 stuck stretch(es) set to missing. (4)
- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-26 19:00:00 | 12068 |
| val | 2017-05-27 20:00:00 | 2017-09-11 15:00:00 | 2562 |
| test | 2017-09-12 16:00:00 | 2017-12-31 23:00:00 | 2562 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 2.552 | 1.745 | 19.449 | -0.129 | 0.621 |
| same_time_yesterday | baseline | 2.552 | 1.745 | 19.449 | -0.129 | 0.621 |
| ridge | ml | 2.575 | 1.871 | 19.623 | -9.052 | 0.615 |
| gbm_change | ml | 3.068 | 2.299 | 23.381 | -13.246 | 0.453 |
| gbm | ml | 3.137 | 2.391 | 23.911 | -14.179 | 0.428 |
| time_of_day_profile | baseline | 5.221 | 4.614 | 39.790 | 31.427 | -0.584 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 3.121 | 3.121 |
| MAE (kWh) | 2.152 | 2.152 |
| CV(RMSE) % | 43.058 | 43.058 |
| NMBE % | -2.140 | -2.140 |
| R² | 0.587 | 0.587 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 43.1% (limit 30%), NMBE -2.1% (limit ±10%): **does not pass**.

90% prediction interval: ±4.32 kWh (width from validation errors); it contained 84% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-06 | 1724 | 0.00 |
| 2017-08-06 to 2017-10-17 | 1724 | 0.00 |
| 2017-10-17 to 2017-12-31 | 1724 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 100% |

> Warning: No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
