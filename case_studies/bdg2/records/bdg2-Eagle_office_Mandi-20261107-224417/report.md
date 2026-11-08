# Run report: bdg2-Eagle_office_Mandi

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 16.1331 for 2 d 13 h (2016-07-16 05:00:00 to 2016-07-18 18:00:00); 6 such stretch(es), 4 d 23 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 6 stuck stretch(es) set to missing. (89)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-22 15:00:00 | 11403 |
| val | 2017-05-23 16:00:00 | 2017-09-01 19:00:00 | 2419 |
| test | 2017-09-02 20:00:00 | 2017-12-31 23:00:00 | 2421 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| towt | baseline | 0.635 | 0.445 | 3.656 | 0.103 | 0.875 |
| time_of_week_profile | baseline | 0.700 | 0.516 | 4.030 | 1.589 | 0.848 |
| time_of_day_profile | baseline | 0.707 | 0.522 | 4.065 | 1.602 | 0.845 |
| ridge | ml | 0.791 | 0.578 | 4.548 | -0.052 | 0.806 |
| same_time_last_week | baseline | 0.855 | 0.592 | 4.922 | 0.258 | 0.773 |
| gbm_change | ml | 1.321 | 0.690 | 7.597 | 1.235 | 0.460 |
| gbm | ml | 1.460 | 0.739 | 8.398 | 1.573 | 0.340 |
| persistence | baseline | 1.497 | 0.946 | 8.613 | 0.077 | 0.306 |
| same_time_yesterday | baseline | 1.497 | 0.946 | 8.613 | 0.077 | 0.306 |

## Test result

Chosen model: **towt** 

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 1.048 | 1.048 |
| MAE (kWh) | 0.849 | 0.849 |
| CV(RMSE) % | 5.888 | 5.888 |
| NMBE % | 4.077 | 4.077 |
| R² | 0.671 | 0.671 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 5.9% (limit 30%), NMBE 4.1% (limit ±10%): **passes**.

90% prediction interval: ±0.895 kWh (width from validation errors); it contained 58% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-22 to 2017-07-29 | 1630 | 0.00 |
| 2017-07-29 to 2017-10-05 | 1629 | 0.00 |
| 2017-10-05 to 2017-12-31 | 1629 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'towt' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
