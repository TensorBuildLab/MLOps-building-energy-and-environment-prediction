# Run report: bdg2-Gator_public_Kendall

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 16.8333 for 3 d 23 h (2017-09-20 00:00:00 to 2017-09-23 23:00:00); 617 such stretch(es), 638 d 7 h in total. The value is unchanged in 96% of steps and changes by at least ~0.3333 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 617 stuck stretch(es) set to missing. (12234)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 2858 |
| val | 2017-05-28 00:00:00 | 2017-09-19 03:00:00 | 598 |
| test | 2017-09-20 04:00:00 | 2017-12-31 05:00:00 | 608 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| time_of_week_profile | baseline | 3.616 | 2.071 | 23.296 | -3.254 | 0.503 |
| time_of_day_profile | baseline | 3.617 | 1.973 | 23.307 | -3.777 | 0.503 |
| gbm | ml | 3.908 | 2.446 | 25.182 | -3.065 | 0.419 |
| towt | baseline | 4.093 | 2.445 | 26.375 | -11.242 | 0.363 |
| ridge | ml | 4.194 | 2.445 | 27.023 | -8.878 | 0.331 |
| gbm_change | ml | 5.457 | 3.327 | 35.159 | -5.678 | -0.132 |
| same_time_last_week | baseline | 5.990 | 3.582 | 38.596 | -5.546 | -0.364 |
| persistence | baseline | 6.026 | 3.612 | 38.828 | -5.097 | -0.380 |
| same_time_yesterday | baseline | 6.026 | 3.612 | 38.828 | -5.097 | -0.380 |

## Test result

Chosen model: **time_of_week_profile** 

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 4.288 | 4.288 |
| MAE (kWh) | 2.949 | 2.949 |
| CV(RMSE) % | 28.955 | 28.955 |
| NMBE % | -2.289 | -2.289 |
| R² | 0.555 | 0.555 |

Skill vs time_of_week_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 29.0% (limit 30%), NMBE -2.3% (limit ±10%): **passes**.

90% prediction interval: ±4.16 kWh (width from validation errors); it contained 85% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-11 | 409 | 0.00 |
| 2017-08-11 to 2017-10-27 | 409 | 0.00 |
| 2017-10-28 to 2017-12-31 | 408 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'time_of_week_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
