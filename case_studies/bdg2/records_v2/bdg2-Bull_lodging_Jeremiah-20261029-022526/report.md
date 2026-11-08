# Run report: bdg2-Bull_lodging_Jeremiah

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 49 for 7 h (2016-06-23 23:00:00 to 2016-06-24 06:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 2 stuck stretch(es) set to missing. (3)
- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-27 02:00:00 | 12047 |
| val | 2017-05-28 03:00:00 | 2017-09-11 19:00:00 | 2557 |
| test | 2017-09-12 20:00:00 | 2017-12-31 23:00:00 | 2558 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 7.065 | 4.069 | 13.477 | 3.477 | 0.766 |
| gbm | ml | 7.103 | 4.307 | 13.549 | 4.265 | 0.763 |
| ridge | ml | 7.606 | 5.023 | 14.510 | 2.368 | 0.729 |
| persistence | baseline | 11.874 | 5.792 | 22.651 | 0.568 | 0.339 |
| same_time_yesterday | baseline | 11.874 | 5.792 | 22.651 | 0.568 | 0.339 |
| time_of_day_profile | baseline | 13.596 | 10.359 | 25.935 | -13.347 | 0.133 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 8.326 | 15.936 |
| MAE (kWh) | 4.599 | 8.974 |
| CV(RMSE) % | 12.986 | 24.855 |
| NMBE % | 0.849 | -0.684 |
| R² | 0.834 | 0.393 |

Skill vs persistence: **0.48** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 13.0% (limit 30%), NMBE 0.8% (limit ±10%): **passes**.

90% prediction interval: ±9.3 kWh (width from validation errors); it contained 89% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-06 | 1721 | 0.33 |
| 2017-08-06 to 2017-10-17 | 1721 | 0.58 |
| 2017-10-17 to 2017-12-31 | 1721 | 0.42 |

Pooled skill: **0.46**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 66% |
| calendar (time of day, weekday) | 33% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
