# Run report: bdg2-Peacock_education_Lyle

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
| train | 2016-01-01 00:00:00 | 2017-05-26 18:00:00 | 12273 |
| val | 2017-05-27 19:00:00 | 2017-09-13 08:00:00 | 2606 |
| test | 2017-09-14 09:00:00 | 2017-12-31 23:00:00 | 2607 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 46.045 | 26.906 | 7.402 | -0.996 | 0.855 |
| gbm_change | ml | 48.222 | 27.761 | 7.752 | -0.589 | 0.841 |
| ridge | ml | 50.601 | 34.523 | 8.134 | -0.041 | 0.825 |
| same_time_last_week | baseline | 60.600 | 37.084 | 9.742 | -0.443 | 0.750 |
| towt | baseline | 72.213 | 54.390 | 11.608 | -8.282 | 0.644 |
| time_of_week_profile | baseline | 80.124 | 64.016 | 12.880 | -10.104 | 0.562 |
| time_of_day_profile | baseline | 80.159 | 64.039 | 12.886 | -10.110 | 0.562 |
| persistence | baseline | 81.945 | 47.716 | 13.173 | 0.177 | 0.542 |
| same_time_yesterday | baseline | 81.945 | 47.716 | 13.173 | 0.177 | 0.542 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 44.490 | 78.972 |
| MAE (kWh) | 30.643 | 52.099 |
| CV(RMSE) % | 7.025 | 12.470 |
| NMBE % | -2.568 | -1.140 |
| R² | 0.882 | 0.627 |

Skill vs same_time_last_week: **0.44** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 7.0% (limit 30%), NMBE -2.6% (limit ±10%): **passes**.

90% prediction interval: ±53 kWh (width from validation errors); it contained 85% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.26 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.27 |
| 2017-10-19 to 2017-12-31 | 1753 | 0.41 |

Pooled skill: **0.34**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 69% |
| calendar (time of day, weekday) | 30% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
