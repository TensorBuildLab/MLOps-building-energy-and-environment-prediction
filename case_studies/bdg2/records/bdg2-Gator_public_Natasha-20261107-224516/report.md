# Run report: bdg2-Gator_public_Natasha

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 45.8333 for 2 d 23 h (2016-01-17 00:00:00 to 2016-01-19 23:00:00); 642 such stretch(es), 642 d 6 h in total. The value is unchanged in 96% of steps and changes by at least ~4.1667 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 642 stuck stretch(es) set to missing. (12204)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-01 01:00:00 | 2947 |
| val | 2017-06-02 02:00:00 | 2017-09-14 02:00:00 | 625 |
| test | 2017-09-15 03:00:00 | 2017-12-30 05:00:00 | 627 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| towt | baseline | 70.021 | 47.587 | 47.884 | 10.263 | 0.384 |
| ridge | ml | 71.049 | 50.323 | 48.587 | 9.520 | 0.366 |
| time_of_week_profile | baseline | 74.067 | 50.228 | 50.651 | 19.760 | 0.311 |
| gbm | ml | 74.294 | 52.217 | 50.806 | 12.945 | 0.307 |
| gbm_change | ml | 80.335 | 55.318 | 54.938 | 13.984 | 0.189 |
| time_of_day_profile | baseline | 86.254 | 68.430 | 58.985 | 20.026 | 0.066 |
| same_time_last_week | baseline | 92.528 | 67.836 | 63.276 | -4.485 | -0.075 |
| persistence | baseline | 102.388 | 71.422 | 70.019 | -2.418 | -0.317 |
| same_time_yesterday | baseline | 102.388 | 71.422 | 70.019 | -2.418 | -0.317 |

## Test result

Chosen model: **towt** 

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 45.181 | 45.181 |
| MAE (kWh) | 33.678 | 33.678 |
| CV(RMSE) % | 39.988 | 39.988 |
| NMBE % | 3.613 | 3.613 |
| R² | 0.624 | 0.624 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 40.0% (limit 30%), NMBE 3.6% (limit ±10%): **does not pass**.

90% prediction interval: ±88.2 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-01 to 2017-08-12 | 422 | 0.00 |
| 2017-08-12 to 2017-10-21 | 421 | 0.00 |
| 2017-10-21 to 2017-12-30 | 421 | 0.00 |

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
