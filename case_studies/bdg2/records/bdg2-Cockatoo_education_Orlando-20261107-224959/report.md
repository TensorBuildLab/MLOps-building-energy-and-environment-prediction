# Run report: bdg2-Cockatoo_education_Orlando

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
| train | 2016-01-01 00:00:00 | 2017-06-09 23:00:00 | 11283 |
| val | 2017-06-11 00:00:00 | 2017-09-21 19:00:00 | 2393 |
| test | 2017-09-22 20:00:00 | 2017-12-31 23:00:00 | 2395 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 21.868 | 12.963 | 9.356 | 2.411 | 0.708 |
| gbm | ml | 21.998 | 13.126 | 9.412 | 2.914 | 0.705 |
| time_of_week_profile | baseline | 22.119 | 15.467 | 9.464 | 0.123 | 0.701 |
| time_of_day_profile | baseline | 22.197 | 15.519 | 9.497 | 0.128 | 0.699 |
| ridge | ml | 23.754 | 16.011 | 10.163 | 2.609 | 0.656 |
| towt | baseline | 25.656 | 19.347 | 10.977 | 5.221 | 0.598 |
| same_time_last_week | baseline | 27.831 | 17.378 | 11.907 | 0.488 | 0.527 |
| persistence | baseline | 32.186 | 18.765 | 13.771 | 0.103 | 0.368 |
| same_time_yesterday | baseline | 32.186 | 18.765 | 13.771 | 0.103 | 0.368 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 21.915 | 29.437 |
| MAE (kWh) | 13.835 | 20.416 |
| CV(RMSE) % | 8.879 | 11.926 |
| NMBE % | 1.498 | 5.685 |
| R² | 0.808 | 0.653 |

Skill vs time_of_week_profile: **0.26** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 8.9% (limit 30%), NMBE 1.5% (limit ±10%): **passes**.

90% prediction interval: ±31.8 kWh (width from validation errors); it contained 87% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-10 to 2017-08-19 | 1612 | 0.01 |
| 2017-08-19 to 2017-10-25 | 1612 | 0.12 |
| 2017-10-25 to 2017-12-31 | 1612 | 0.26 |

Pooled skill: **0.16**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 81% |
| calendar (time of day, weekday) | 17% |
| airTemperature | 2% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
