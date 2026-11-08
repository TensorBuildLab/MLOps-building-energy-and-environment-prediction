# Run report: bdg2-Peacock_office_Norman

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 17 h (2016-01-08 15:00:00 to 2016-01-09 08:00:00); 48 such stretch(es), 14 d 14 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 48 stuck stretch(es) set to missing. (110)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (58)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (11)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (65)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 20:00:00 | 12266 |
| val | 2017-05-27 21:00:00 | 2017-09-13 08:00:00 | 2604 |
| test | 2017-09-14 09:00:00 | 2017-12-31 23:00:00 | 2606 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 4.707 | 3.554 | 14.980 | -3.780 | 0.450 |
| gbm_change | ml | 4.739 | 3.454 | 15.083 | -2.819 | 0.443 |
| ridge | ml | 4.819 | 3.631 | 15.337 | -2.035 | 0.424 |
| same_time_last_week | baseline | 5.992 | 4.247 | 19.070 | 0.234 | 0.109 |
| same_time_yesterday | baseline | 6.216 | 4.292 | 19.783 | 0.409 | 0.041 |
| persistence | baseline | 6.216 | 4.292 | 19.783 | 0.409 | 0.041 |
| towt | baseline | 7.871 | 6.159 | 25.052 | -16.276 | -0.538 |
| time_of_day_profile | baseline | 8.298 | 6.649 | 26.410 | -18.342 | -0.709 |
| time_of_week_profile | baseline | 8.326 | 6.620 | 26.500 | -18.387 | -0.720 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 5.377 | 8.359 |
| MAE (kWh) | 3.982 | 6.000 |
| CV(RMSE) % | 14.324 | 22.266 |
| NMBE % | -0.129 | -0.072 |
| R² | 0.647 | 0.148 |

Skill vs same_time_last_week: **0.36** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.3% (limit 30%), NMBE -0.1% (limit ±10%): **passes**.

90% prediction interval: ±7.37 kWh (width from validation errors); it contained 86% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1753 | 0.24 |
| 2017-08-07 to 2017-10-19 | 1753 | 0.24 |
| 2017-10-20 to 2017-12-31 | 1752 | 0.36 |

Pooled skill: **0.31**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 51% |
| calendar (time of day, weekday) | 48% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
