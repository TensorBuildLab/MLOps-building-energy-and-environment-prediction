# Run report: bdg2-Robin_office_Antonina

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 12280 |
| val | 2017-05-27 16:00:00 | 2017-09-13 06:00:00 | 2607 |
| test | 2017-09-14 07:00:00 | 2017-12-31 23:00:00 | 2609 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| time_of_week_profile | baseline | 89.593 | 51.474 | 21.509 | -0.606 | 0.463 |
| time_of_day_profile | baseline | 90.345 | 51.705 | 21.689 | -0.595 | 0.454 |
| towt | baseline | 92.197 | 44.945 | 22.134 | -6.919 | 0.432 |
| gbm | ml | 92.742 | 48.156 | 22.265 | -5.461 | 0.425 |
| gbm_change | ml | 92.798 | 46.223 | 22.278 | -5.102 | 0.424 |
| ridge | ml | 95.174 | 54.911 | 22.848 | -1.314 | 0.394 |
| same_time_last_week | baseline | 114.960 | 61.276 | 27.598 | -0.035 | 0.117 |
| persistence | baseline | 132.994 | 77.904 | 31.928 | 0.251 | -0.182 |
| same_time_yesterday | baseline | 132.994 | 77.904 | 31.928 | 0.251 | -0.182 |

## Test result

Chosen model: **time_of_week_profile** 

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 40.296 | 40.296 |
| MAE (kWh) | 28.058 | 28.058 |
| CV(RMSE) % | 10.051 | 10.051 |
| NMBE % | -4.367 | -4.367 |
| R² | 0.693 | 0.693 |

Skill vs time_of_week_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 10.1% (limit 30%), NMBE -4.4% (limit ±10%): **passes**.

90% prediction interval: ±130 kWh (width from validation errors); it contained 98% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.00 |
| 2017-08-07 to 2017-10-19 | 1755 | 0.00 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'time_of_week_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
