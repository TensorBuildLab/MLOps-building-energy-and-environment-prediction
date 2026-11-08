# Run report: bdg2-Peacock_lodging_Sergio

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
| gbm_change | ml | 9.731 | 7.191 | 12.438 | -2.112 | 0.480 |
| gbm | ml | 9.734 | 7.400 | 12.442 | -3.066 | 0.480 |
| ridge | ml | 9.911 | 7.439 | 12.668 | -1.980 | 0.461 |
| persistence | baseline | 11.062 | 7.979 | 14.139 | -0.048 | 0.328 |
| same_time_yesterday | baseline | 11.062 | 7.979 | 14.139 | -0.048 | 0.328 |
| same_time_last_week | baseline | 15.256 | 10.646 | 19.499 | -1.743 | -0.278 |
| towt | baseline | 21.737 | 18.186 | 27.784 | -21.863 | -1.594 |
| time_of_week_profile | baseline | 26.053 | 23.094 | 33.301 | -28.826 | -2.727 |
| time_of_day_profile | baseline | 26.054 | 23.144 | 33.302 | -28.835 | -2.727 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 12.261 | 14.061 |
| MAE (kWh) | 8.951 | 9.996 |
| CV(RMSE) % | 13.260 | 15.207 |
| NMBE % | -2.948 | -0.227 |
| R² | 0.639 | 0.525 |

Skill vs persistence: **0.13** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 13.3% (limit 30%), NMBE -2.9% (limit ±10%): **passes**.

90% prediction interval: ±15.7 kWh (width from validation errors); it contained 83% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.12 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.15 |
| 2017-10-19 to 2017-12-31 | 1753 | 0.12 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 86% |
| calendar (time of day, weekday) | 14% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
