# Run report: bdg2-Gator_public_Maude

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 95.8333 for 3 d 23 h (2016-10-26 00:00:00 to 2016-10-29 23:00:00); 532 such stretch(es), 624 d 20 h in total. The value is unchanged in 97% of steps and changes by at least ~2.5 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 532 stuck stretch(es) set to missing. (12336)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-04 02:00:00 | 2485 |
| val | 2017-06-05 03:00:00 | 2017-09-17 00:00:00 | 526 |
| test | 2017-09-18 01:00:00 | 2017-12-31 05:00:00 | 527 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| towt | baseline | 19.966 | 11.838 | 17.610 | 3.836 | -0.016 |
| ridge | ml | 21.396 | 13.145 | 18.871 | 4.851 | -0.166 |
| time_of_week_profile | baseline | 23.772 | 18.494 | 20.966 | 11.137 | -0.440 |
| time_of_day_profile | baseline | 23.779 | 18.585 | 20.973 | 11.269 | -0.440 |
| gbm_change | ml | 25.741 | 18.398 | 22.703 | 4.965 | -0.688 |
| persistence | baseline | 26.315 | 14.892 | 23.210 | 2.717 | -0.764 |
| same_time_yesterday | baseline | 26.315 | 14.892 | 23.210 | 2.717 | -0.764 |
| same_time_last_week | baseline | 29.989 | 16.075 | 26.451 | 2.938 | -1.291 |
| gbm | ml | 32.670 | 21.300 | 28.815 | 4.718 | -1.719 |

## Test result

Chosen model: **towt** 

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 25.874 | 25.874 |
| MAE (kWh) | 16.106 | 16.106 |
| CV(RMSE) % | 28.709 | 28.709 |
| NMBE % | 1.207 | 1.207 |
| R² | 0.521 | 0.521 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 28.7% (limit 30%), NMBE 1.2% (limit ±10%): **passes**.

90% prediction interval: ±18 kWh (width from validation errors); it contained 78% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-04 to 2017-08-13 | 355 | 0.00 |
| 2017-08-13 to 2017-10-25 | 355 | 0.00 |
| 2017-10-25 to 2017-12-31 | 355 | 0.00 |

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
