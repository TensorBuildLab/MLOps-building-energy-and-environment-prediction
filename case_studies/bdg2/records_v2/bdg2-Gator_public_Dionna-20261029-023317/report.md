# Run report: bdg2-Gator_public_Dionna

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 11.6667 for 4 d 23 h (2017-12-13 00:00:00 to 2017-12-17 23:00:00); 569 such stretch(es), 646 d 7 h in total. The value is unchanged in 96% of steps and changes by at least ~0.3333 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 569 stuck stretch(es) set to missing. (12666)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-15 01:00:00 | 2640 |
| val | 2017-05-16 02:00:00 | 2017-08-31 02:00:00 | 559 |
| test | 2017-09-01 03:00:00 | 2017-12-30 05:00:00 | 561 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| time_of_day_profile | baseline | 3.623 | 2.162 | 22.838 | -11.300 | 0.449 |
| gbm | ml | 3.774 | 2.585 | 23.796 | -8.034 | 0.402 |
| ridge | ml | 4.179 | 2.554 | 26.344 | -9.566 | 0.267 |
| gbm_change | ml | 4.489 | 2.886 | 28.298 | -8.032 | 0.155 |
| persistence | baseline | 5.673 | 3.445 | 35.767 | -6.293 | -0.351 |
| same_time_yesterday | baseline | 5.673 | 3.445 | 35.767 | -6.293 | -0.351 |

## Test result

Chosen model: **time_of_day_profile** 

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 5.933 | 5.933 |
| MAE (kWh) | 4.582 | 4.582 |
| CV(RMSE) % | 46.842 | 46.842 |
| NMBE % | -33.206 | -33.206 |
| R² | -0.230 | -0.230 |

Skill vs time_of_day_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 46.8% (limit 30%), NMBE -33.2% (limit ±10%): **does not pass**.

90% prediction interval: ±3.59 kWh (width from validation errors); it contained 44% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-15 to 2017-07-30 | 378 | 0.00 |
| 2017-07-30 to 2017-10-10 | 377 | 0.00 |
| 2017-10-10 to 2017-12-30 | 377 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
