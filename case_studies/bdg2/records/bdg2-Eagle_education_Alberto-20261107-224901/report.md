# Run report: bdg2-Eagle_education_Alberto

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 438.566 for 2 d 13 h (2016-07-16 05:00:00 to 2016-07-18 18:00:00); 6 such stretch(es), 4 d 23 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
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
| train | 2016-01-01 00:00:00 | 2017-05-22 01:00:00 | 11435 |
| val | 2017-05-23 02:00:00 | 2017-09-01 13:00:00 | 2426 |
| test | 2017-09-02 14:00:00 | 2017-12-31 23:00:00 | 2427 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| time_of_week_profile | baseline | 18.238 | 12.797 | 3.965 | -0.161 | 0.847 |
| time_of_day_profile | baseline | 18.423 | 13.013 | 4.005 | -0.153 | 0.844 |
| towt | baseline | 18.916 | 13.673 | 4.112 | 1.086 | 0.835 |
| same_time_last_week | baseline | 22.919 | 15.715 | 4.982 | 0.331 | 0.758 |
| ridge | ml | 23.703 | 17.606 | 5.153 | 1.286 | 0.742 |
| same_time_yesterday | baseline | 36.665 | 22.801 | 7.970 | 0.082 | 0.382 |
| persistence | baseline | 36.665 | 22.801 | 7.970 | 0.082 | 0.382 |
| gbm_change | ml | 43.428 | 28.466 | 9.441 | 3.085 | 0.133 |
| gbm | ml | 48.822 | 29.503 | 10.613 | 3.563 | -0.096 |

## Test result

Chosen model: **time_of_week_profile** 

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 32.174 | 32.174 |
| MAE (kWh) | 25.546 | 25.546 |
| CV(RMSE) % | 6.677 | 6.677 |
| NMBE % | 4.536 | 4.536 |
| R² | 0.568 | 0.568 |

Skill vs time_of_week_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 6.7% (limit 30%), NMBE 4.5% (limit ±10%): **passes**.

90% prediction interval: ±26.8 kWh (width from validation errors); it contained 57% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-22 to 2017-07-29 | 1634 | 0.00 |
| 2017-07-29 to 2017-10-05 | 1634 | 0.00 |
| 2017-10-05 to 2017-12-31 | 1633 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'time_of_week_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
