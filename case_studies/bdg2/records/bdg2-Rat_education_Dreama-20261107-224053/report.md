# Run report: bdg2-Rat_education_Dreama

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 18.3 for 11 h (2016-10-01 20:00:00 to 2016-10-02 07:00:00); 51 such stretch(es), 15 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2016-08-07 22:00:00 to 2016-08-08 04:00:00); 2 such stretch(es), 12 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 51 stuck stretch(es) set to missing. (107)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (60)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (12)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (16)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-15 07:00:00 | 12005 |
| val | 2017-05-16 08:00:00 | 2017-08-30 12:00:00 | 2548 |
| test | 2017-08-31 13:00:00 | 2017-12-31 23:00:00 | 2549 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 26.280 | 15.912 | 27.714 | -2.900 | 0.602 |
| persistence | baseline | 27.154 | 13.516 | 28.636 | -0.781 | 0.575 |
| same_time_yesterday | baseline | 27.154 | 13.516 | 28.636 | -0.781 | 0.575 |
| ridge | ml | 27.310 | 15.438 | 28.801 | -0.572 | 0.570 |
| gbm | ml | 31.055 | 19.472 | 32.750 | -4.896 | 0.444 |
| time_of_day_profile | baseline | 41.272 | 30.078 | 43.524 | 2.297 | 0.017 |
| time_of_week_profile | baseline | 41.278 | 30.103 | 43.531 | 2.289 | 0.017 |
| towt | baseline | 41.308 | 26.990 | 43.563 | -4.383 | 0.015 |
| same_time_last_week | baseline | 54.867 | 36.883 | 57.862 | 0.958 | -0.737 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 12.523 | 12.970 |
| MAE (kWh) | 5.870 | 5.703 |
| CV(RMSE) % | 13.978 | 14.477 |
| NMBE % | 1.438 | 1.002 |
| R² | 0.591 | 0.561 |

Skill vs persistence: **0.03** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.0% (limit 30%), NMBE 1.4% (limit ±10%): **passes**.

90% prediction interval: ±36 kWh (width from validation errors); it contained 99% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-15 to 2017-07-25 | 1715 | 0.06 |
| 2017-07-25 to 2017-10-05 | 1715 | -0.02 |
| 2017-10-05 to 2017-12-31 | 1715 | 0.08 |

Pooled skill: **0.04**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 97% |
| calendar (time of day, weekday) | 2% |
| dewTemperature | 1% |

> Warning: The model is barely better than persistence on test data (skill 0.03).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
