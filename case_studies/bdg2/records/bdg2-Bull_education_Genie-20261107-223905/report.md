# Run report: bdg2-Bull_education_Genie

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 92 for 6 h (2017-06-18 23:00:00 to 2017-06-19 05:00:00); 2 such stretch(es), 12 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 2 stuck stretch(es) set to missing. (2)
- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-27 01:00:00 | 12052 |
| val | 2017-05-28 02:00:00 | 2017-09-11 17:00:00 | 2558 |
| test | 2017-09-12 18:00:00 | 2017-12-31 23:00:00 | 2560 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 8.458 | 5.134 | 7.276 | -0.992 | 0.895 |
| gbm_change | ml | 8.749 | 4.908 | 7.527 | -0.797 | 0.887 |
| ridge | ml | 10.366 | 6.956 | 8.918 | 0.172 | 0.842 |
| same_time_last_week | baseline | 11.466 | 6.391 | 9.864 | 0.962 | 0.806 |
| towt | baseline | 14.565 | 11.049 | 12.530 | -8.256 | 0.687 |
| time_of_day_profile | baseline | 14.673 | 11.161 | 12.622 | -8.157 | 0.683 |
| time_of_week_profile | baseline | 14.779 | 10.975 | 12.714 | -8.173 | 0.678 |
| persistence | baseline | 17.116 | 9.634 | 14.725 | 0.291 | 0.568 |
| same_time_yesterday | baseline | 17.116 | 9.634 | 14.725 | 0.291 | 0.568 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 13.623 | 22.020 |
| MAE (kWh) | 5.967 | 10.735 |
| CV(RMSE) % | 10.546 | 17.047 |
| NMBE % | -0.089 | -2.082 |
| R² | 0.876 | 0.675 |

Skill vs same_time_last_week: **0.38** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 10.5% (limit 30%), NMBE -0.1% (limit ±10%): **passes**.

90% prediction interval: ±10.5 kWh (width from validation errors); it contained 87% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-06 | 1722 | 0.22 |
| 2017-08-06 to 2017-10-17 | 1722 | 0.27 |
| 2017-10-17 to 2017-12-31 | 1722 | 0.39 |

Pooled skill: **0.35**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 74% |
| calendar (time of day, weekday) | 25% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
