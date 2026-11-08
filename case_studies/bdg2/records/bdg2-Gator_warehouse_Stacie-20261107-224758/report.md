# Run report: bdg2-Gator_warehouse_Stacie

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 21.6667 for 3 d 23 h (2017-06-16 00:00:00 to 2017-06-19 23:00:00); 597 such stretch(es), 636 d 3 h in total. The value is unchanged in 96% of steps and changes by at least ~0.6666 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 597 stuck stretch(es) set to missing. (12282)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-02 00:00:00 | 2017-05-21 05:00:00 | 2758 |
| val | 2017-05-24 00:00:00 | 2017-09-08 02:00:00 | 585 |
| test | 2017-09-10 00:00:00 | 2017-12-31 05:00:00 | 588 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| towt | baseline | 5.162 | 3.640 | 21.365 | 6.094 | 0.343 |
| ridge | ml | 5.182 | 3.298 | 21.446 | 0.527 | 0.338 |
| gbm | ml | 5.711 | 3.930 | 23.637 | 2.458 | 0.195 |
| gbm_change | ml | 6.641 | 4.622 | 27.487 | 3.983 | -0.088 |
| same_time_yesterday | baseline | 6.876 | 4.545 | 28.460 | 0.820 | -0.166 |
| persistence | baseline | 6.876 | 4.545 | 28.460 | 0.820 | -0.166 |
| time_of_week_profile | baseline | 7.587 | 6.760 | 31.403 | 23.835 | -0.420 |
| time_of_day_profile | baseline | 7.664 | 6.782 | 31.722 | 23.868 | -0.449 |
| same_time_last_week | baseline | 7.810 | 4.944 | 32.325 | 1.272 | -0.505 |

## Test result

Chosen model: **towt** 

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 4.889 | 4.889 |
| MAE (kWh) | 2.881 | 2.881 |
| CV(RMSE) % | 29.031 | 29.031 |
| NMBE % | -9.961 | -9.961 |
| R² | 0.549 | 0.549 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 29.0% (limit 30%), NMBE -10.0% (limit ±10%): **passes**.

90% prediction interval: ±6.3 kWh (width from validation errors); it contained 90% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-22 to 2017-08-04 | 394 | 0.00 |
| 2017-08-04 to 2017-10-19 | 394 | 0.00 |
| 2017-10-19 to 2017-12-31 | 394 | 0.00 |

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
