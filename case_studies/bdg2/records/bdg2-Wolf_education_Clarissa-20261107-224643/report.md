# Run report: bdg2-Wolf_education_Clarissa

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3 for 14 h (2016-11-02 19:00:00 to 2016-11-03 09:00:00); 51 such stretch(es), 14 d 10 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `windSpeed`: 51 stuck stretch(es) set to missing. (90)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (20)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (20)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (70)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 12278 |
| val | 2017-05-27 16:00:00 | 2017-09-13 06:00:00 | 2607 |
| test | 2017-09-14 07:00:00 | 2017-12-31 23:00:00 | 2608 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 7.974 | 5.105 | 16.006 | -2.321 | 0.566 |
| gbm | ml | 8.277 | 5.481 | 16.614 | -3.078 | 0.532 |
| ridge | ml | 8.825 | 6.195 | 17.714 | -2.522 | 0.468 |
| towt | baseline | 9.216 | 6.381 | 18.499 | -3.616 | 0.420 |
| time_of_day_profile | baseline | 9.639 | 7.348 | 19.348 | -6.969 | 0.366 |
| time_of_week_profile | baseline | 9.728 | 7.390 | 19.528 | -6.974 | 0.354 |
| same_time_yesterday | baseline | 10.720 | 6.484 | 21.518 | 0.113 | 0.216 |
| persistence | baseline | 10.720 | 6.484 | 21.518 | 0.113 | 0.216 |
| same_time_last_week | baseline | 12.100 | 7.422 | 24.289 | 0.293 | 0.001 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 7.765 | 10.745 |
| MAE (kWh) | 5.359 | 7.651 |
| CV(RMSE) % | 14.751 | 20.413 |
| NMBE % | -0.569 | -1.347 |
| R² | 0.743 | 0.508 |

Skill vs towt: **0.28** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.8% (limit 30%), NMBE -0.6% (limit ±10%): **passes**.

90% prediction interval: ±12.9 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.14 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.11 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.33 |

Pooled skill: **0.21**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 52% |
| electricity (recent history) | 47% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
