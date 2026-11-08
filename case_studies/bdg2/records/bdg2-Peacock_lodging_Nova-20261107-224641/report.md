# Run report: bdg2-Peacock_lodging_Nova

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 9 for 9 h (2016-08-27 20:00:00 to 2016-08-28 05:00:00); 6 such stretch(es), 1 d 18 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 17 h (2016-01-08 15:00:00 to 2016-01-09 08:00:00); 48 such stretch(es), 14 d 14 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 6 stuck stretch(es) set to missing. (12)
- mask_stuck `airTemperature`: 48 stuck stretch(es) set to missing. (110)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (58)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (11)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (65)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 20:00:00 | 12255 |
| val | 2017-05-27 21:00:00 | 2017-09-13 10:00:00 | 2602 |
| test | 2017-09-14 11:00:00 | 2017-12-31 23:00:00 | 2603 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 3.018 | 1.844 | 25.006 | -1.284 | 0.376 |
| gbm_change | ml | 3.101 | 1.851 | 25.697 | -1.212 | 0.341 |
| ridge | ml | 3.132 | 2.173 | 25.946 | -1.583 | 0.328 |
| persistence | baseline | 3.482 | 1.954 | 28.851 | -0.017 | 0.169 |
| same_time_yesterday | baseline | 3.482 | 1.954 | 28.851 | -0.017 | 0.169 |
| same_time_last_week | baseline | 4.744 | 3.038 | 39.301 | -2.364 | -0.542 |
| towt | baseline | 7.126 | 6.073 | 59.038 | -46.116 | -2.480 |
| time_of_day_profile | baseline | 9.418 | 8.530 | 78.034 | -68.837 | -5.080 |
| time_of_week_profile | baseline | 9.437 | 8.522 | 78.184 | -68.788 | -5.103 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 3.847 | 5.024 |
| MAE (kWh) | 2.896 | 3.617 |
| CV(RMSE) % | 19.691 | 25.714 |
| NMBE % | -1.193 | -0.402 |
| R² | 0.606 | 0.328 |

Skill vs persistence: **0.23** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 19.7% (limit 30%), NMBE -1.2% (limit ±10%): **passes**.

90% prediction interval: ±4.88 kWh (width from validation errors); it contained 80% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1751 | 0.11 |
| 2017-08-07 to 2017-10-19 | 1751 | 0.24 |
| 2017-10-19 to 2017-12-31 | 1751 | 0.23 |

Pooled skill: **0.20**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 74% |
| calendar (time of day, weekday) | 25% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
