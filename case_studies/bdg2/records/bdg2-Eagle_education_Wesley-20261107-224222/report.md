# Run report: bdg2-Eagle_education_Wesley

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 120 for 2 d 13 h (2016-07-16 05:00:00 to 2016-07-18 18:00:00); 7 such stretch(es), 5 d 10 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 7 stuck stretch(es) set to missing. (95)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-29 16:00:00 | 12089 |
| val | 2017-05-30 17:00:00 | 2017-09-14 22:00:00 | 2566 |
| test | 2017-09-15 23:00:00 | 2017-12-31 23:00:00 | 2567 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 13.865 | 10.033 | 13.292 | 2.647 | 0.899 |
| gbm_change | ml | 14.112 | 9.660 | 13.528 | 1.338 | 0.896 |
| ridge | ml | 14.675 | 11.224 | 14.068 | 0.683 | 0.887 |
| same_time_last_week | baseline | 17.131 | 11.878 | 16.423 | 1.028 | 0.846 |
| same_time_yesterday | baseline | 18.586 | 12.597 | 17.818 | 0.301 | 0.819 |
| persistence | baseline | 18.586 | 12.597 | 17.818 | 0.301 | 0.819 |
| towt | baseline | 39.380 | 31.470 | 37.752 | -26.404 | 0.188 |
| time_of_day_profile | baseline | 40.868 | 32.795 | 39.179 | -28.269 | 0.125 |
| time_of_week_profile | baseline | 40.887 | 32.792 | 39.196 | -28.312 | 0.125 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 13.688 | 21.720 |
| MAE (kWh) | 9.764 | 14.591 |
| CV(RMSE) % | 10.837 | 17.196 |
| NMBE % | 1.836 | -0.590 |
| R² | 0.905 | 0.760 |

Skill vs same_time_last_week: **0.37** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 10.8% (limit 30%), NMBE 1.8% (limit ±10%): **passes**.

90% prediction interval: ±22 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-29 to 2017-08-09 | 1727 | 0.28 |
| 2017-08-09 to 2017-10-21 | 1727 | 0.26 |
| 2017-10-21 to 2017-12-31 | 1727 | 0.40 |

Pooled skill: **0.32**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 88% |
| calendar (time of day, weekday) | 12% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
