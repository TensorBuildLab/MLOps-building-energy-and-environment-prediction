# Run report: bdg2-Bull_education_Roseann

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-28 05:00:00 | 11986 |
| val | 2017-05-29 06:00:00 | 2017-09-12 09:00:00 | 2544 |
| test | 2017-09-13 10:00:00 | 2017-12-31 23:00:00 | 2545 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 7.306 | 4.030 | 2.809 | 0.597 | 0.848 |
| gbm_change | ml | 8.639 | 4.285 | 3.322 | 0.546 | 0.787 |
| ridge | ml | 9.118 | 6.169 | 3.506 | 0.529 | 0.763 |
| same_time_last_week | baseline | 9.590 | 4.646 | 3.688 | -0.128 | 0.738 |
| time_of_day_profile | baseline | 12.312 | 10.681 | 4.734 | 3.782 | 0.568 |
| time_of_week_profile | baseline | 12.433 | 10.746 | 4.781 | 3.781 | 0.560 |
| persistence | baseline | 12.560 | 6.332 | 4.830 | 0.055 | 0.551 |
| same_time_yesterday | baseline | 12.560 | 6.332 | 4.830 | 0.055 | 0.551 |
| towt | baseline | 13.017 | 11.394 | 5.005 | 4.045 | 0.518 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 27.170 | 36.199 |
| MAE (kWh) | 9.948 | 14.092 |
| CV(RMSE) % | 10.979 | 14.627 |
| NMBE % | -1.634 | -1.837 |
| R² | 0.406 | -0.055 |

Skill vs same_time_last_week: **0.25** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.0% (limit 30%), NMBE -1.6% (limit ±10%): **passes**.

90% prediction interval: ±8.16 kWh (width from validation errors); it contained 69% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-28 to 2017-08-07 | 1713 | 0.08 |
| 2017-08-07 to 2017-10-18 | 1712 | 0.30 |
| 2017-10-18 to 2017-12-31 | 1712 | 0.24 |

Pooled skill: **0.24**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 74% |
| calendar (time of day, weekday) | 25% |
| windSpeed | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
