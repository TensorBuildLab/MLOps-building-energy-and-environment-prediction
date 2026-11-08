# Run report: bdg2-Gator_public_Lindsey

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 29.1667 for 6 d 23 h (2016-04-20 00:00:00 to 2016-04-26 23:00:00); 525 such stretch(es), 653 d 3 h in total. The value is unchanged in 97% of steps and changes by at least ~0.4167 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 525 stuck stretch(es) set to missing. (13050)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-03 05:00:00 | 2590 |
| val | 2017-05-05 00:00:00 | 2017-08-22 02:00:00 | 555 |
| test | 2017-08-23 03:00:00 | 2017-12-29 05:00:00 | 549 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| towt | baseline | 5.830 | 3.330 | 23.973 | -1.828 | 0.657 |
| time_of_day_profile | baseline | 5.892 | 3.529 | 24.226 | 1.768 | 0.650 |
| time_of_week_profile | baseline | 5.903 | 3.521 | 24.270 | 1.806 | 0.648 |
| gbm | ml | 6.172 | 3.977 | 25.378 | -2.403 | 0.615 |
| ridge | ml | 7.291 | 4.784 | 29.980 | -3.126 | 0.463 |
| gbm_change | ml | 8.849 | 6.357 | 36.386 | -2.425 | 0.210 |
| same_time_last_week | baseline | 10.654 | 7.098 | 43.806 | -10.273 | -0.146 |
| persistence | baseline | 10.656 | 7.249 | 43.813 | -8.074 | -0.146 |
| same_time_yesterday | baseline | 10.656 | 7.249 | 43.813 | -8.074 | -0.146 |

## Test result

Chosen model: **towt** 

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 7.383 | 7.383 |
| MAE (kWh) | 4.427 | 4.427 |
| CV(RMSE) % | 33.016 | 33.016 |
| NMBE % | -12.116 | -12.116 |
| R² | 0.277 | 0.277 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 33.0% (limit 30%), NMBE -12.1% (limit ±10%): **does not pass**.

90% prediction interval: ±5.13 kWh (width from validation errors); it contained 77% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-05 to 2017-07-23 | 370 | 0.00 |
| 2017-07-23 to 2017-10-01 | 370 | 0.00 |
| 2017-10-01 to 2017-12-29 | 370 | 0.00 |

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
