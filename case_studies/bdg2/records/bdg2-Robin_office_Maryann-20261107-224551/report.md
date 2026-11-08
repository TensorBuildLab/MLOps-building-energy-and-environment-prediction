# Run report: bdg2-Robin_office_Maryann

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
| time_of_day_profile | baseline | 70.785 | 34.586 | 32.766 | -9.683 | 0.297 |
| time_of_week_profile | baseline | 71.011 | 34.681 | 32.870 | -9.681 | 0.293 |
| towt | baseline | 71.402 | 33.746 | 33.051 | -10.765 | 0.285 |
| gbm | ml | 72.114 | 38.178 | 33.381 | -7.377 | 0.271 |
| ridge | ml | 72.249 | 43.353 | 33.444 | -0.969 | 0.268 |
| same_time_last_week | baseline | 77.653 | 39.383 | 35.945 | -0.054 | 0.154 |
| gbm_change | ml | 78.147 | 42.691 | 36.174 | -5.703 | 0.144 |
| persistence | baseline | 104.821 | 58.987 | 48.521 | 0.155 | -0.541 |
| same_time_yesterday | baseline | 104.821 | 58.987 | 48.521 | 0.155 | -0.541 |

## Test result

Chosen model: **time_of_day_profile** 

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 24.630 | 24.630 |
| MAE (kWh) | 18.958 | 18.958 |
| CV(RMSE) % | 11.300 | 11.300 |
| NMBE % | -6.955 | -6.955 |
| R² | 0.648 | 0.648 |

Skill vs time_of_day_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.3% (limit 30%), NMBE -7.0% (limit ±10%): **passes**.

90% prediction interval: ±196 kWh (width from validation errors); it contained 100% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.00 |
| 2017-08-07 to 2017-10-19 | 1755 | 0.00 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
