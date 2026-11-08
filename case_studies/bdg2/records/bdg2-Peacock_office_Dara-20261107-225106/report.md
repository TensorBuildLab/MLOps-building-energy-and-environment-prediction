# Run report: bdg2-Peacock_office_Dara

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
| train | 2016-01-01 00:00:00 | 2017-05-27 03:00:00 | 12254 |
| val | 2017-05-28 04:00:00 | 2017-09-13 12:00:00 | 2601 |
| test | 2017-09-14 13:00:00 | 2017-12-31 23:00:00 | 2603 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 27.020 | 20.215 | 20.254 | -3.904 | 0.730 |
| gbm | ml | 27.494 | 20.545 | 20.608 | -4.290 | 0.721 |
| ridge | ml | 28.269 | 21.433 | 21.190 | -3.205 | 0.705 |
| persistence | baseline | 34.477 | 23.949 | 25.843 | 0.168 | 0.561 |
| same_time_yesterday | baseline | 34.477 | 23.949 | 25.843 | 0.168 | 0.561 |
| same_time_last_week | baseline | 34.938 | 24.062 | 26.189 | 0.654 | 0.549 |
| towt | baseline | 36.829 | 27.980 | 27.606 | -13.258 | 0.499 |
| time_of_week_profile | baseline | 46.600 | 37.008 | 34.930 | -24.055 | 0.197 |
| time_of_day_profile | baseline | 46.663 | 37.175 | 34.977 | -24.170 | 0.195 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 26.510 | 33.492 |
| MAE (kWh) | 20.064 | 24.960 |
| CV(RMSE) % | 14.977 | 18.922 |
| NMBE % | 2.201 | 0.171 |
| R² | 0.834 | 0.735 |

Skill vs persistence: **0.21** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 15.0% (limit 30%), NMBE 2.2% (limit ±10%): **passes**.

90% prediction interval: ±43.5 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-08 | 1751 | 0.25 |
| 2017-08-08 to 2017-10-20 | 1751 | 0.17 |
| 2017-10-20 to 2017-12-31 | 1750 | 0.22 |

Pooled skill: **0.22**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 78% |
| calendar (time of day, weekday) | 22% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
