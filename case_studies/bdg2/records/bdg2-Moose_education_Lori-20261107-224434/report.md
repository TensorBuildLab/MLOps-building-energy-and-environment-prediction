# Run report: bdg2-Moose_education_Lori

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 160.592 for 2 d 13 h (2016-08-28 16:00:00 to 2016-08-31 05:00:00); 304 such stretch(es), 138 d 14 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 304 stuck stretch(es) set to missing. (1806)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (165)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (209)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (170)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-15 16:00:00 | 10952 |
| val | 2017-06-16 17:00:00 | 2017-09-21 11:00:00 | 2323 |
| test | 2017-09-22 12:00:00 | 2017-12-31 23:00:00 | 2324 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 5.728 | 3.745 | 3.137 | 0.004 | 0.536 |
| same_time_yesterday | baseline | 5.728 | 3.745 | 3.137 | 0.004 | 0.536 |
| gbm_change | ml | 6.033 | 4.305 | 3.304 | 0.958 | 0.485 |
| gbm | ml | 6.368 | 4.594 | 3.488 | 0.526 | 0.426 |
| same_time_last_week | baseline | 8.696 | 6.024 | 4.762 | -0.116 | -0.070 |
| ridge | ml | 12.706 | 10.795 | 6.958 | 5.803 | -1.284 |
| towt | baseline | 18.546 | 15.817 | 10.157 | 8.283 | -3.866 |
| time_of_day_profile | baseline | 25.712 | 23.183 | 14.082 | -12.486 | -8.353 |
| time_of_week_profile | baseline | 25.976 | 23.327 | 14.226 | -12.538 | -8.546 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 13.043 | 13.043 |
| MAE (kWh) | 9.506 | 9.506 |
| CV(RMSE) % | 6.008 | 6.008 |
| NMBE % | 0.378 | 0.378 |
| R² | 0.820 | 0.820 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 6.0% (limit 30%), NMBE 0.4% (limit ±10%): **passes**.

90% prediction interval: ±9.05 kWh (width from validation errors); it contained 59% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-15 to 2017-08-19 | 1565 | 0.00 |
| 2017-08-19 to 2017-10-27 | 1565 | 0.00 |
| 2017-10-27 to 2017-12-31 | 1565 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 100% |

> Warning: No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
