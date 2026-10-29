# Run report: bdg2-Wolf_office_Elisabeth

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3 for 14 h (2016-11-02 19:00:00 to 2016-11-03 09:00:00); 51 such stretch(es), 14 d 10 h in total. | prepare() treats these stretches as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `windSpeed`: 51 stuck stretch(es) set to missing. (90)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (20)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (20)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (70)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 12279 |
| val | 2017-05-27 16:00:00 | 2017-09-13 06:00:00 | 2607 |
| test | 2017-09-14 07:00:00 | 2017-12-31 23:00:00 | 2608 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| time_of_day_profile | baseline | 8.132 | 6.023 | 6.056 | -1.716 | 0.477 |
| ridge | ml | 8.206 | 6.090 | 6.111 | -1.517 | 0.468 |
| gbm_change | ml | 8.232 | 5.848 | 6.130 | -1.879 | 0.464 |
| gbm | ml | 8.835 | 6.364 | 6.579 | -2.254 | 0.383 |
| persistence | baseline | 10.084 | 6.779 | 7.509 | -0.080 | 0.196 |
| same_time_yesterday | baseline | 10.084 | 6.779 | 7.509 | -0.080 | 0.196 |

## Test result

Chosen model: **time_of_day_profile** 

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 11.201 | 11.201 |
| MAE (kWh) | 8.740 | 8.740 |
| CV(RMSE) % | 8.600 | 8.600 |
| NMBE % | -4.586 | -4.586 |
| R² | -0.084 | -0.084 |

Skill vs time_of_day_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 8.6% (limit 30%), NMBE -4.6% (limit ±10%): **passes**.

90% prediction interval: ±13.1 kWh (width from validation errors); it contained 80% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.00 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.00 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
