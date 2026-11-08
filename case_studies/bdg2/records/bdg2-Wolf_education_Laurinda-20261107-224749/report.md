# Run report: bdg2-Wolf_education_Laurinda

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3 for 14 h (2016-11-02 19:00:00 to 2016-11-03 09:00:00); 51 such stretch(es), 14 d 10 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

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
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 12280 |
| val | 2017-05-27 16:00:00 | 2017-09-13 06:00:00 | 2607 |
| test | 2017-09-14 07:00:00 | 2017-12-31 23:00:00 | 2608 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 62.892 | 38.689 | 31.489 | -5.286 | 0.592 |
| gbm | ml | 65.382 | 42.261 | 32.736 | -8.098 | 0.559 |
| ridge | ml | 69.813 | 51.520 | 34.955 | -9.080 | 0.497 |
| towt | baseline | 70.789 | 48.911 | 35.443 | -10.983 | 0.483 |
| time_of_day_profile | baseline | 71.953 | 51.345 | 36.026 | -13.473 | 0.466 |
| time_of_week_profile | baseline | 72.629 | 51.719 | 36.364 | -13.481 | 0.456 |
| same_time_yesterday | baseline | 83.375 | 47.604 | 41.744 | -0.071 | 0.283 |
| persistence | baseline | 83.375 | 47.604 | 41.744 | -0.071 | 0.283 |
| same_time_last_week | baseline | 90.469 | 53.187 | 45.296 | -1.132 | 0.156 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 54.195 | 69.700 |
| MAE (kWh) | 35.752 | 50.953 |
| CV(RMSE) % | 28.853 | 37.107 |
| NMBE % | -7.368 | -19.634 |
| R² | 0.696 | 0.497 |

Skill vs towt: **0.22** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 28.9% (limit 30%), NMBE -7.4% (limit ±10%): **passes**.

90% prediction interval: ±102 kWh (width from validation errors); it contained 92% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.08 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.17 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.26 |

Pooled skill: **0.17**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 59% |
| electricity (recent history) | 41% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
