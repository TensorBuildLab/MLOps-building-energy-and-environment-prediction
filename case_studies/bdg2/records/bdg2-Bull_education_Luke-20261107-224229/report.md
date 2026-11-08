# Run report: bdg2-Bull_education_Luke

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-27 02:00:00 | 12053 |
| val | 2017-05-28 03:00:00 | 2017-09-11 18:00:00 | 2558 |
| test | 2017-09-12 19:00:00 | 2017-12-31 23:00:00 | 2560 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 31.648 | 19.188 | 11.908 | -3.973 | 0.692 |
| ridge | ml | 34.786 | 20.742 | 13.089 | -0.232 | 0.628 |
| gbm_change | ml | 36.058 | 18.879 | 13.567 | -2.916 | 0.601 |
| same_time_last_week | baseline | 40.505 | 19.180 | 15.240 | 1.415 | 0.496 |
| same_time_yesterday | baseline | 53.139 | 27.398 | 19.994 | 0.420 | 0.132 |
| persistence | baseline | 53.139 | 27.398 | 19.994 | 0.420 | 0.132 |
| towt | baseline | 53.445 | 43.038 | 20.109 | -15.088 | 0.122 |
| time_of_week_profile | baseline | 54.873 | 44.474 | 20.646 | -15.718 | 0.075 |
| time_of_day_profile | baseline | 54.932 | 44.614 | 20.668 | -15.747 | 0.073 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 34.523 | 56.236 |
| MAE (kWh) | 19.034 | 31.399 |
| CV(RMSE) % | 11.595 | 18.887 |
| NMBE % | -2.857 | -2.886 |
| R² | 0.822 | 0.527 |

Skill vs same_time_last_week: **0.39** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.6% (limit 30%), NMBE -2.9% (limit ±10%): **passes**.

90% prediction interval: ±34.6 kWh (width from validation errors); it contained 89% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-06 | 1722 | 0.17 |
| 2017-08-06 to 2017-10-17 | 1722 | 0.23 |
| 2017-10-17 to 2017-12-31 | 1722 | 0.41 |

Pooled skill: **0.32**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 66% |
| calendar (time of day, weekday) | 34% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
