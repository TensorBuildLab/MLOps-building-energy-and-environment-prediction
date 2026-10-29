# Run report: bdg2-Bobcat_other_Timothy

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -6.1 for 12 h (2017-01-01 16:00:00 to 2017-01-02 04:00:00); 19 such stretch(es), 5 d 13 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 6 h (2017-02-26 01:00:00 to 2017-02-26 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing. |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 16.5, 14.9 at 2016-02-18 03:00:00. | prepare() treats them as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 19 stuck stretch(es) set to missing. (38)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (35)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (122)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-07 23:00:00 | 11531 |
| val | 2017-06-09 00:00:00 | 2017-09-19 06:00:00 | 2447 |
| test | 2017-09-20 07:00:00 | 2017-12-31 23:00:00 | 2448 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 2.394 | 1.626 | 15.076 | 3.969 | 0.736 |
| gbm_change | ml | 2.399 | 1.590 | 15.110 | 3.667 | 0.735 |
| ridge | ml | 2.753 | 1.994 | 17.334 | 4.568 | 0.651 |
| persistence | baseline | 3.564 | 2.255 | 22.442 | -0.088 | 0.415 |
| same_time_yesterday | baseline | 3.564 | 2.255 | 22.442 | -0.088 | 0.415 |
| time_of_day_profile | baseline | 4.579 | 3.960 | 28.836 | -23.110 | 0.034 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 4.768 | 6.215 |
| MAE (kWh) | 3.428 | 4.162 |
| CV(RMSE) % | 20.837 | 27.163 |
| NMBE % | 0.640 | 0.361 |
| R² | 0.640 | 0.389 |

Skill vs persistence: **0.23** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 20.8% (limit 30%), NMBE 0.6% (limit ±10%): **passes**.

90% prediction interval: ±3.44 kWh (width from validation errors); it contained 61% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-08 to 2017-08-15 | 1648 | 0.32 |
| 2017-08-15 to 2017-10-23 | 1648 | 0.18 |
| 2017-10-23 to 2017-12-31 | 1647 | 0.27 |

Pooled skill: **0.25**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 58% |
| calendar (time of day, weekday) | 41% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
