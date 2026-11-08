# Run report: bdg2-Gator_public_Nettie

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 18.3333 for 3 d 23 h (2016-02-02 00:00:00 to 2016-02-05 23:00:00); 560 such stretch(es), 642 d 16 h in total. The value is unchanged in 97% of steps and changes by at least ~0.3333 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 560 stuck stretch(es) set to missing. (12624)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-15 00:00:00 | 2585 |
| val | 2017-05-16 01:00:00 | 2017-09-07 02:00:00 | 548 |
| test | 2017-09-08 03:00:00 | 2017-12-31 05:00:00 | 549 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| towt | baseline | 3.338 | 2.191 | 19.585 | 5.404 | 0.389 |
| gbm | ml | 3.515 | 2.489 | 20.623 | 1.222 | 0.322 |
| ridge | ml | 3.633 | 2.567 | 21.312 | 6.477 | 0.276 |
| time_of_day_profile | baseline | 3.697 | 2.825 | 21.686 | 11.038 | 0.250 |
| time_of_week_profile | baseline | 3.833 | 2.940 | 22.485 | 11.263 | 0.194 |
| gbm_change | ml | 4.284 | 3.015 | 25.133 | 7.008 | -0.007 |
| same_time_yesterday | baseline | 4.669 | 3.028 | 27.392 | 1.168 | -0.196 |
| persistence | baseline | 4.669 | 3.028 | 27.392 | 1.168 | -0.196 |
| same_time_last_week | baseline | 5.407 | 3.509 | 31.722 | 1.490 | -0.604 |

## Test result

Chosen model: **towt** 

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 4.717 | 4.717 |
| MAE (kWh) | 2.940 | 2.940 |
| CV(RMSE) % | 36.664 | 36.664 |
| NMBE % | -14.673 | -14.673 |
| R² | 0.142 | 0.142 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 36.7% (limit 30%), NMBE -14.7% (limit ±10%): **does not pass**.

90% prediction interval: ±3.97 kWh (width from validation errors); it contained 80% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-15 to 2017-08-03 | 370 | 0.00 |
| 2017-08-03 to 2017-10-18 | 370 | 0.00 |
| 2017-10-18 to 2017-12-31 | 369 | 0.00 |

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
