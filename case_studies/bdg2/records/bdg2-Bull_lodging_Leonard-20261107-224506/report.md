# Run report: bdg2-Bull_lodging_Leonard

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 32 for 14 h (2016-07-22 23:00:00 to 2016-07-23 13:00:00); 39 such stretch(es), 12 d 10 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 39 stuck stretch(es) set to missing. (103)
- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-27 13:00:00 | 11978 |
| val | 2017-05-28 14:00:00 | 2017-09-11 22:00:00 | 2542 |
| test | 2017-09-12 23:00:00 | 2017-12-31 23:00:00 | 2544 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 2.627 | 1.654 | 8.493 | 0.205 | 0.709 |
| gbm_change | ml | 2.860 | 1.692 | 9.247 | 0.387 | 0.655 |
| ridge | ml | 2.917 | 1.888 | 9.431 | 0.772 | 0.641 |
| persistence | baseline | 3.317 | 1.872 | 10.722 | 0.083 | 0.536 |
| same_time_yesterday | baseline | 3.317 | 1.872 | 10.722 | 0.083 | 0.536 |
| same_time_last_week | baseline | 4.308 | 2.952 | 13.926 | 1.812 | 0.217 |
| towt | baseline | 5.228 | 3.938 | 16.900 | -6.826 | -0.153 |
| time_of_day_profile | baseline | 6.205 | 5.034 | 20.059 | -11.939 | -0.624 |
| time_of_week_profile | baseline | 6.216 | 5.041 | 20.095 | -11.962 | -0.630 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 3.855 | 4.961 |
| MAE (kWh) | 2.591 | 3.286 |
| CV(RMSE) % | 10.479 | 13.485 |
| NMBE % | 2.031 | -0.298 |
| R² | 0.640 | 0.404 |

Skill vs persistence: **0.22** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 10.5% (limit 30%), NMBE 2.0% (limit ±10%): **passes**.

90% prediction interval: ±3.59 kWh (width from validation errors); it contained 75% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-07 | 1712 | 0.05 |
| 2017-08-07 to 2017-10-17 | 1711 | 0.24 |
| 2017-10-17 to 2017-12-31 | 1711 | 0.22 |

Pooled skill: **0.22**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 69% |
| calendar (time of day, weekday) | 31% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
