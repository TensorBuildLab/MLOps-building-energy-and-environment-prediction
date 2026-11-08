# Run report: bdg2-Hog_warehouse_Louise

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 11 for 12 h (2016-01-16 21:00:00 to 2016-01-17 09:00:00); 78 such stretch(es), 23 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 78 stuck stretch(es) set to missing. (181)
- mask_stuck `airTemperature`: 58 stuck stretch(es) set to missing. (149)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (62)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (11)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-27 08:00:00 | 12153 |
| val | 2017-05-28 09:00:00 | 2017-09-13 09:00:00 | 2580 |
| test | 2017-09-14 10:00:00 | 2017-12-31 23:00:00 | 2581 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 3.568 | 2.472 | 32.296 | 0.721 | 0.711 |
| gbm_change | ml | 3.605 | 2.516 | 32.631 | 0.495 | 0.705 |
| ridge | ml | 3.829 | 2.748 | 34.663 | 1.979 | 0.668 |
| towt | baseline | 4.210 | 3.012 | 38.108 | -0.644 | 0.598 |
| time_of_week_profile | baseline | 4.331 | 3.071 | 39.203 | -10.357 | 0.575 |
| same_time_last_week | baseline | 4.340 | 2.972 | 39.286 | 0.269 | 0.573 |
| time_of_day_profile | baseline | 4.423 | 3.136 | 40.042 | -10.467 | 0.556 |
| persistence | baseline | 5.682 | 3.840 | 51.432 | 0.192 | 0.268 |
| same_time_yesterday | baseline | 5.682 | 3.840 | 51.432 | 0.192 | 0.268 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 3.277 | 4.645 |
| MAE (kWh) | 2.339 | 3.698 |
| CV(RMSE) % | 29.100 | 41.241 |
| NMBE % | -1.011 | -10.501 |
| R² | 0.865 | 0.729 |

Skill vs towt: **0.29** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 29.1% (limit 30%), NMBE -1.0% (limit ±10%): **passes**.

90% prediction interval: ±6.02 kWh (width from validation errors); it contained 93% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-08 | 1737 | 0.12 |
| 2017-08-08 to 2017-10-19 | 1736 | 0.31 |
| 2017-10-19 to 2017-12-31 | 1736 | 0.26 |

Pooled skill: **0.24**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 58% |
| calendar (time of day, weekday) | 40% |
| airTemperature | 3% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
