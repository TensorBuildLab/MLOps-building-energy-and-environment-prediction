# Run report: bdg2-Bull_education_Pablo

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 23 for 10 h (2016-11-27 02:00:00 to 2016-11-27 12:00:00); 20 such stretch(es), 5 d 14 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 20 stuck stretch(es) set to missing. (34)
- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-27 05:00:00 | 12026 |
| val | 2017-05-28 06:00:00 | 2017-09-11 17:00:00 | 2553 |
| test | 2017-09-12 18:00:00 | 2017-12-31 23:00:00 | 2553 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 3.420 | 2.390 | 9.030 | 3.459 | 0.913 |
| gbm_change | ml | 3.793 | 2.537 | 10.014 | 2.440 | 0.893 |
| ridge | ml | 4.037 | 2.910 | 10.658 | 1.179 | 0.879 |
| same_time_last_week | baseline | 4.087 | 2.578 | 10.790 | 1.144 | 0.876 |
| time_of_week_profile | baseline | 4.133 | 2.772 | 10.914 | 0.896 | 0.873 |
| time_of_day_profile | baseline | 4.322 | 2.916 | 11.411 | 0.898 | 0.861 |
| towt | baseline | 4.420 | 3.035 | 11.670 | 3.167 | 0.855 |
| persistence | baseline | 7.233 | 4.356 | 19.098 | 0.304 | 0.611 |
| same_time_yesterday | baseline | 7.233 | 4.356 | 19.098 | 0.304 | 0.611 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 5.727 | 8.340 |
| MAE (kWh) | 3.326 | 4.698 |
| CV(RMSE) % | 13.699 | 19.949 |
| NMBE % | 2.429 | -1.206 |
| R² | 0.845 | 0.670 |

Skill vs same_time_last_week: **0.31** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 13.7% (limit 30%), NMBE 2.4% (limit ±10%): **passes**.

90% prediction interval: ±4.99 kWh (width from validation errors); it contained 81% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-06 | 1718 | 0.18 |
| 2017-08-06 to 2017-10-17 | 1718 | 0.15 |
| 2017-10-17 to 2017-12-31 | 1718 | 0.34 |

Pooled skill: **0.29**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 71% |
| calendar (time of day, weekday) | 28% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
