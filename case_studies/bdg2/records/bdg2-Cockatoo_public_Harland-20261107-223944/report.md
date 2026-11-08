# Run report: bdg2-Cockatoo_public_Harland

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -1.7 for 14 h (2017-01-28 16:00:00 to 2017-01-29 06:00:00); 57 such stretch(es), 16 d 11 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.6 for 8 h (2016-09-07 02:00:00 to 2016-09-07 10:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 57 stuck stretch(es) set to missing. (108)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (323)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (273)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (306)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-09 20:00:00 | 11274 |
| val | 2017-06-10 21:00:00 | 2017-09-21 15:00:00 | 2392 |
| test | 2017-09-22 16:00:00 | 2017-12-31 23:00:00 | 2393 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 3.986 | 2.548 | 8.087 | -0.182 | 0.863 |
| gbm_change | ml | 4.109 | 2.591 | 8.336 | -0.249 | 0.855 |
| towt | baseline | 4.464 | 3.151 | 9.056 | -3.606 | 0.829 |
| time_of_week_profile | baseline | 4.585 | 3.327 | 9.302 | -4.566 | 0.819 |
| time_of_day_profile | baseline | 4.615 | 3.339 | 9.363 | -4.553 | 0.817 |
| ridge | ml | 4.617 | 3.302 | 9.367 | 0.274 | 0.817 |
| same_time_last_week | baseline | 5.498 | 3.503 | 11.153 | 0.376 | 0.740 |
| persistence | baseline | 7.780 | 4.893 | 15.783 | 0.138 | 0.479 |
| same_time_yesterday | baseline | 7.780 | 4.893 | 15.783 | 0.138 | 0.479 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 4.311 | 10.002 |
| MAE (kWh) | 3.029 | 5.817 |
| CV(RMSE) % | 8.960 | 20.789 |
| NMBE % | -2.741 | -6.681 |
| R² | 0.876 | 0.330 |

Skill vs towt: **0.57** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 9.0% (limit 30%), NMBE -2.7% (limit ±10%): **passes**.

90% prediction interval: ±5.09 kWh (width from validation errors); it contained 83% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-09 to 2017-08-19 | 1611 | 0.16 |
| 2017-08-19 to 2017-10-25 | 1611 | 0.09 |
| 2017-10-25 to 2017-12-31 | 1611 | 0.58 |

Pooled skill: **0.46**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 57% |
| calendar (time of day, weekday) | 42% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
