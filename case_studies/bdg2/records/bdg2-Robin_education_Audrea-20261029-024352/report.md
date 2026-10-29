# Run report: bdg2-Robin_education_Audrea

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 296.056 for 43 d 10 h (2016-03-08 13:00:00 to 2016-04-20 23:00:00); 20 such stretch(es), 122 d 2 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 20 stuck stretch(es) set to missing. (2830)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-19 00:00:00 | 10299 |
| val | 2017-06-20 01:00:00 | 2017-09-20 11:00:00 | 2183 |
| test | 2017-09-21 12:00:00 | 2017-12-31 23:00:00 | 2184 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 21.393 | 13.302 | 7.595 | -0.324 | 0.436 |
| persistence | baseline | 23.728 | 14.674 | 8.424 | 0.056 | 0.306 |
| same_time_yesterday | baseline | 23.728 | 14.674 | 8.424 | 0.056 | 0.306 |
| gbm_change | ml | 25.566 | 18.012 | 9.077 | -1.453 | 0.195 |
| gbm | ml | 26.777 | 18.472 | 9.507 | -0.059 | 0.116 |
| time_of_day_profile | baseline | 27.287 | 20.458 | 9.688 | -5.701 | 0.082 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 21.844 | 22.624 |
| MAE (kWh) | 15.303 | 14.919 |
| CV(RMSE) % | 9.635 | 9.979 |
| NMBE % | -2.463 | -1.037 |
| R² | 0.864 | 0.854 |

Skill vs persistence: **0.03** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 9.6% (limit 30%), NMBE -2.5% (limit ±10%): **passes**.

90% prediction interval: ±27 kWh (width from validation errors); it contained 86% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-19 to 2017-08-20 | 1472 | 0.10 |
| 2017-08-20 to 2017-10-21 | 1472 | 0.20 |
| 2017-10-21 to 2017-12-31 | 1471 | -0.05 |

Pooled skill: **0.07**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 94% |
| calendar (time of day, weekday) | 6% |

> Warning: The model is barely better than persistence on test data (skill 0.03).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
