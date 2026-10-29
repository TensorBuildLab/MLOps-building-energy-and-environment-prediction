# Run report: bdg2-Eagle_education_Samantha

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 306.922 for 2 d 8 h (2016-07-16 05:00:00 to 2016-07-18 13:00:00); 5 such stretch(es), 4 d 23 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 5 stuck stretch(es) set to missing. (94)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-27 04:00:00 | 12205 |
| val | 2017-05-28 05:00:00 | 2017-09-13 21:00:00 | 2591 |
| test | 2017-09-14 22:00:00 | 2017-12-31 23:00:00 | 2593 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| time_of_day_profile | baseline | 25.019 | 13.944 | 9.339 | -0.804 | 0.264 |
| ridge | ml | 27.124 | 17.599 | 10.125 | -3.954 | 0.135 |
| gbm_change | ml | 27.917 | 17.300 | 10.421 | -2.871 | 0.084 |
| gbm | ml | 28.898 | 18.335 | 10.787 | -3.721 | 0.019 |
| persistence | baseline | 31.916 | 19.904 | 11.914 | 0.068 | -0.197 |
| same_time_yesterday | baseline | 31.916 | 19.904 | 11.914 | 0.068 | -0.197 |

## Test result

Chosen model: **time_of_day_profile** 

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 24.640 | 24.640 |
| MAE (kWh) | 19.276 | 19.276 |
| CV(RMSE) % | 9.729 | 9.729 |
| NMBE % | -6.393 | -6.393 |
| R² | -0.293 | -0.293 |

Skill vs time_of_day_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 9.7% (limit 30%), NMBE -6.4% (limit ±10%): **passes**.

90% prediction interval: ±26.5 kWh (width from validation errors); it contained 73% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-07 | 1744 | 0.00 |
| 2017-08-07 to 2017-10-20 | 1744 | 0.00 |
| 2017-10-20 to 2017-12-31 | 1744 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
