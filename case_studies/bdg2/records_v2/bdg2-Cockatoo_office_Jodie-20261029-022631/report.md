# Run report: bdg2-Cockatoo_office_Jodie

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -1.7 for 14 h (2017-01-28 16:00:00 to 2017-01-29 06:00:00); 57 such stretch(es), 16 d 11 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.6 for 8 h (2016-09-07 02:00:00 to 2016-09-07 10:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 57 stuck stretch(es) set to missing. (108)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (323)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (273)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (306)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-09 22:00:00 | 11279 |
| val | 2017-06-10 23:00:00 | 2017-09-21 20:00:00 | 2392 |
| test | 2017-09-22 21:00:00 | 2017-12-31 23:00:00 | 2394 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 3.466 | 2.370 | 7.281 | -0.757 | 0.790 |
| gbm_change | ml | 3.602 | 2.327 | 7.566 | -0.509 | 0.773 |
| ridge | ml | 4.402 | 3.310 | 9.247 | 0.909 | 0.660 |
| time_of_day_profile | baseline | 6.420 | 5.609 | 13.486 | -11.372 | 0.278 |
| persistence | baseline | 7.376 | 4.283 | 15.494 | -0.013 | 0.047 |
| same_time_yesterday | baseline | 7.376 | 4.283 | 15.494 | -0.013 | 0.047 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 6.813 | 10.844 |
| MAE (kWh) | 4.925 | 7.874 |
| CV(RMSE) % | 12.032 | 19.152 |
| NMBE % | 2.535 | 8.385 |
| R² | 0.698 | 0.234 |

Skill vs time_of_day_profile: **0.37** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 12.0% (limit 30%), NMBE 2.5% (limit ±10%): **passes**.

90% prediction interval: ±5.68 kWh (width from validation errors); it contained 67% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-09 to 2017-08-19 | 1612 | 0.51 |
| 2017-08-19 to 2017-10-25 | 1611 | 0.33 |
| 2017-10-25 to 2017-12-31 | 1611 | 0.39 |

Pooled skill: **0.41**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 60% |
| calendar (time of day, weekday) | 32% |
| airTemperature | 5% |
| dewTemperature | 2% |
| windSpeed | 2% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
