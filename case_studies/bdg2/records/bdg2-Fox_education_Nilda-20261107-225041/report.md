# Run report: bdg2-Fox_education_Nilda

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10.6 for 9 h (2017-02-18 21:00:00 to 2017-02-19 06:00:00); 6 such stretch(es), 1 d 18 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 7 h (2017-08-26 00:00:00 to 2017-08-26 07:00:00); 1 such stretch(es), 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 6 stuck stretch(es) set to missing. (12)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (8)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (2)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (14)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 16:00:00 | 12278 |
| val | 2017-05-27 17:00:00 | 2017-09-13 07:00:00 | 2607 |
| test | 2017-09-14 08:00:00 | 2017-12-31 23:00:00 | 2608 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 11.239 | 8.009 | 7.758 | 2.172 | 0.896 |
| gbm_change | ml | 11.395 | 8.138 | 7.866 | 2.010 | 0.893 |
| ridge | ml | 11.694 | 8.919 | 8.073 | 1.021 | 0.887 |
| persistence | baseline | 15.453 | 9.891 | 10.667 | 0.203 | 0.803 |
| same_time_yesterday | baseline | 15.453 | 9.891 | 10.667 | 0.203 | 0.803 |
| same_time_last_week | baseline | 16.864 | 12.417 | 11.642 | 0.650 | 0.766 |
| time_of_day_profile | baseline | 18.183 | 14.047 | 12.552 | 7.604 | 0.728 |
| time_of_week_profile | baseline | 18.189 | 14.029 | 12.556 | 7.618 | 0.728 |
| towt | baseline | 19.950 | 15.079 | 13.772 | 8.312 | 0.672 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 11.396 | 18.103 |
| MAE (kWh) | 8.013 | 11.574 |
| CV(RMSE) % | 8.408 | 13.356 |
| NMBE % | -0.395 | -0.436 |
| R² | 0.902 | 0.753 |

Skill vs persistence: **0.37** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 8.4% (limit 30%), NMBE -0.4% (limit ±10%): **passes**.

90% prediction interval: ±18 kWh (width from validation errors); it contained 90% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.19 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.42 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.37 |

Pooled skill: **0.33**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 67% |
| calendar (time of day, weekday) | 33% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
