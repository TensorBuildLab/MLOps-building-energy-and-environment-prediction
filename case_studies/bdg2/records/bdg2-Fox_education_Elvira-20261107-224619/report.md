# Run report: bdg2-Fox_education_Elvira

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10.6 for 9 h (2017-02-18 21:00:00 to 2017-02-19 06:00:00); 6 such stretch(es), 1 d 18 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 7 h (2017-08-26 00:00:00 to 2017-08-26 07:00:00); 1 such stretch(es), 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 6 stuck stretch(es) set to missing. (12)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (8)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (2)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (14)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 22:00:00 | 12265 |
| val | 2017-05-27 23:00:00 | 2017-09-13 10:00:00 | 2604 |
| test | 2017-09-14 11:00:00 | 2017-12-31 23:00:00 | 2605 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 12.124 | 8.164 | 7.390 | -1.930 | 0.914 |
| gbm | ml | 12.528 | 8.752 | 7.637 | -2.061 | 0.908 |
| ridge | ml | 13.742 | 9.909 | 8.377 | -0.494 | 0.889 |
| same_time_last_week | baseline | 14.905 | 9.833 | 9.086 | 0.544 | 0.869 |
| same_time_yesterday | baseline | 21.941 | 12.615 | 13.375 | 0.283 | 0.717 |
| persistence | baseline | 21.941 | 12.615 | 13.375 | 0.283 | 0.717 |
| time_of_day_profile | baseline | 37.058 | 33.403 | 22.590 | -20.166 | 0.193 |
| time_of_week_profile | baseline | 37.138 | 33.369 | 22.639 | -20.185 | 0.190 |
| towt | baseline | 38.868 | 36.629 | 23.693 | -22.305 | 0.112 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 18.128 | 24.277 |
| MAE (kWh) | 11.909 | 15.026 |
| CV(RMSE) % | 10.283 | 13.771 |
| NMBE % | 0.617 | 1.041 |
| R² | 0.874 | 0.773 |

Skill vs same_time_last_week: **0.25** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 10.3% (limit 30%), NMBE 0.6% (limit ±10%): **passes**.

90% prediction interval: ±16.6 kWh (width from validation errors); it contained 78% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1753 | 0.07 |
| 2017-08-08 to 2017-10-19 | 1752 | 0.27 |
| 2017-10-20 to 2017-12-31 | 1752 | 0.27 |

Pooled skill: **0.24**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 79% |
| calendar (time of day, weekday) | 20% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
