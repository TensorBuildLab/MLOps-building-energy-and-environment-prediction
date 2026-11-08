# Run report: bdg2-Gator_office_Julie

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 10 for 4 d 23 h (2016-10-18 00:00:00 to 2016-10-22 23:00:00); 528 such stretch(es), 629 d in total. The value is unchanged in 97% of steps and changes by at least ~0.6667 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 528 stuck stretch(es) set to missing. (12456)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-31 00:00:00 | 2753 |
| val | 2017-06-01 01:00:00 | 2017-09-09 02:00:00 | 584 |
| test | 2017-09-10 03:00:00 | 2017-12-30 05:00:00 | 585 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 2.935 | 2.325 | 31.179 | 12.101 | 0.432 |
| ridge | ml | 3.127 | 2.484 | 33.223 | 10.095 | 0.355 |
| towt | baseline | 3.180 | 2.545 | 33.789 | 16.545 | 0.332 |
| gbm_change | ml | 3.494 | 2.876 | 37.125 | 7.527 | 0.194 |
| time_of_week_profile | baseline | 3.720 | 3.139 | 39.519 | 26.185 | 0.087 |
| time_of_day_profile | baseline | 3.958 | 3.215 | 42.053 | 26.764 | -0.034 |
| same_time_last_week | baseline | 4.068 | 2.892 | 43.222 | 1.791 | -0.092 |
| persistence | baseline | 4.087 | 3.252 | 43.423 | 0.581 | -0.103 |
| same_time_yesterday | baseline | 4.087 | 3.252 | 43.423 | 0.581 | -0.103 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 2.179 | 2.442 |
| MAE (kWh) | 1.573 | 1.786 |
| CV(RMSE) % | 30.861 | 34.572 |
| NMBE % | -6.377 | 1.959 |
| R² | 0.653 | 0.564 |

Skill vs towt: **0.11** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 30.9% (limit 30%), NMBE -6.4% (limit ±10%): **does not pass**.

90% prediction interval: ±4.62 kWh (width from validation errors); it contained 95% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-31 to 2017-08-05 | 394 | -0.01 |
| 2017-08-05 to 2017-10-11 | 394 | 0.15 |
| 2017-10-11 to 2017-12-30 | 393 | 0.08 |

Pooled skill: **0.08**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 69% |
| dewTemperature | 17% |
| electricity (recent history) | 13% |
| windSpeed | 1% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
