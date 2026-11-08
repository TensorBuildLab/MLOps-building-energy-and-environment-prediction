# Run report: bdg2-Bull_education_Matilda

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 73 for 8 h (2016-12-25 00:00:00 to 2016-12-25 08:00:00); 4 such stretch(es), 1 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 4 stuck stretch(es) set to missing. (6)
- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-06-11 12:00:00 | 11199 |
| val | 2017-06-12 13:00:00 | 2017-09-19 13:00:00 | 2375 |
| test | 2017-09-20 14:00:00 | 2017-12-31 23:00:00 | 2377 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 13.094 | 8.474 | 18.836 | -2.723 | 0.729 |
| persistence | baseline | 14.329 | 8.297 | 20.613 | 0.791 | 0.676 |
| same_time_yesterday | baseline | 14.329 | 8.297 | 20.613 | 0.791 | 0.676 |
| gbm | ml | 15.297 | 9.841 | 22.005 | -1.859 | 0.631 |
| ridge | ml | 16.177 | 12.991 | 23.271 | -11.332 | 0.587 |
| same_time_last_week | baseline | 16.882 | 10.369 | 24.285 | 4.475 | 0.550 |
| towt | baseline | 31.803 | 26.273 | 45.750 | -29.585 | -0.597 |
| time_of_day_profile | baseline | 40.210 | 34.643 | 57.843 | -44.516 | -1.553 |
| time_of_week_profile | baseline | 40.421 | 34.585 | 58.146 | -44.516 | -1.580 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 70.795 | 73.052 |
| MAE (kWh) | 14.613 | 13.980 |
| CV(RMSE) % | 72.367 | 74.674 |
| NMBE % | -0.030 | -0.722 |
| R² | -0.105 | -0.176 |

Skill vs persistence: **0.03** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 72.4% (limit 30%), NMBE -0.0% (limit ±10%): **does not pass**.

90% prediction interval: ±18.2 kWh (width from validation errors); it contained 80% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-11 to 2017-08-17 | 1600 | 0.03 |
| 2017-08-17 to 2017-10-22 | 1600 | 0.11 |
| 2017-10-22 to 2017-12-31 | 1600 | 0.03 |

Pooled skill: **0.03**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 99% |
| calendar (time of day, weekday) | 1% |

> Warning: The model is barely better than persistence on test data (skill 0.03).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
