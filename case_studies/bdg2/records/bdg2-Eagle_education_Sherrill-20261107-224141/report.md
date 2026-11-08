# Run report: bdg2-Eagle_education_Sherrill

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 638.346 for 3 d 5 h (2016-07-16 05:00:00 to 2016-07-19 10:00:00); 4 such stretch(es), 5 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 4 stuck stretch(es) set to missing. (108)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-28 10:00:00 | 12140 |
| val | 2017-05-29 11:00:00 | 2017-09-14 10:00:00 | 2577 |
| test | 2017-09-15 11:00:00 | 2017-12-31 23:00:00 | 2579 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 24.729 | 18.044 | 3.628 | -1.371 | 0.869 |
| ridge | ml | 26.387 | 19.680 | 3.871 | -0.320 | 0.851 |
| gbm_change | ml | 27.736 | 19.386 | 4.069 | -1.329 | 0.835 |
| time_of_week_profile | baseline | 30.067 | 22.711 | 4.411 | -2.510 | 0.806 |
| time_of_day_profile | baseline | 30.295 | 22.781 | 4.444 | -2.506 | 0.803 |
| towt | baseline | 30.341 | 23.054 | 4.451 | -2.700 | 0.803 |
| same_time_last_week | baseline | 31.303 | 22.228 | 4.592 | -0.141 | 0.790 |
| persistence | baseline | 45.695 | 29.124 | 6.703 | 0.025 | 0.552 |
| same_time_yesterday | baseline | 45.695 | 29.124 | 6.703 | 0.025 | 0.552 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 22.527 | 27.907 |
| MAE (kWh) | 14.789 | 18.009 |
| CV(RMSE) % | 3.268 | 4.049 |
| NMBE % | 0.007 | -0.805 |
| R² | 0.873 | 0.805 |

Skill vs time_of_week_profile: **0.19** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 3.3% (limit 30%), NMBE 0.0% (limit ±10%): **passes**.

90% prediction interval: ±36.9 kWh (width from validation errors); it contained 95% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-28 to 2017-08-09 | 1735 | 0.09 |
| 2017-08-09 to 2017-10-20 | 1735 | 0.22 |
| 2017-10-20 to 2017-12-31 | 1734 | 0.22 |

Pooled skill: **0.19**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 59% |
| calendar (time of day, weekday) | 40% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
