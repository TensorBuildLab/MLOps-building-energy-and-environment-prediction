# Run report: bdg2-Gator_public_Jayme

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 23.875 for 1 d 23 h (2017-03-16 00:00:00 to 2017-03-17 23:00:00); 679 such stretch(es), 656 d 17 h in total. The value is unchanged in 96% of steps and changes by at least ~0.5335 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 679 stuck stretch(es) set to missing. (12366)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-31 03:00:00 | 3152 |
| val | 2017-06-01 04:00:00 | 2017-09-19 00:00:00 | 669 |
| test | 2017-09-20 01:00:00 | 2017-12-31 05:00:00 | 671 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| time_of_day_profile | baseline | 18.448 | 11.785 | 18.671 | 5.149 | 0.535 |
| time_of_week_profile | baseline | 18.520 | 11.865 | 18.744 | 5.219 | 0.531 |
| ridge | ml | 21.315 | 12.838 | 21.573 | -4.556 | 0.379 |
| towt | baseline | 21.511 | 13.134 | 21.771 | -11.651 | 0.367 |
| gbm | ml | 22.598 | 14.739 | 22.871 | -9.264 | 0.302 |
| gbm_change | ml | 27.958 | 16.821 | 28.296 | -8.006 | -0.069 |
| same_time_yesterday | baseline | 29.385 | 15.908 | 29.740 | -4.196 | -0.180 |
| persistence | baseline | 29.385 | 15.908 | 29.740 | -4.196 | -0.180 |
| same_time_last_week | baseline | 31.529 | 18.275 | 31.910 | -2.056 | -0.359 |

## Test result

Chosen model: **time_of_day_profile** 

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 25.102 | 25.102 |
| MAE (kWh) | 17.413 | 17.413 |
| CV(RMSE) % | 33.699 | 33.699 |
| NMBE % | -20.683 | -20.683 |
| R² | 0.287 | 0.287 |

Skill vs time_of_day_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 33.7% (limit 30%), NMBE -20.7% (limit ±10%): **does not pass**.

90% prediction interval: ±22.4 kWh (width from validation errors); it contained 74% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-31 to 2017-08-13 | 451 | 0.00 |
| 2017-08-13 to 2017-10-25 | 451 | 0.00 |
| 2017-10-26 to 2017-12-31 | 450 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
