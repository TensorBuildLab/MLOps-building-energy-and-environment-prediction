# Run report: bdg2-Fox_office_Yong

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
| train | 2016-01-01 00:00:00 | 2017-05-26 18:00:00 | 12273 |
| val | 2017-05-27 19:00:00 | 2017-09-13 08:00:00 | 2606 |
| test | 2017-09-14 09:00:00 | 2017-12-31 23:00:00 | 2607 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 12.099 | 7.617 | 10.610 | -4.156 | 0.870 |
| gbm_change | ml | 12.388 | 7.383 | 10.864 | -1.558 | 0.864 |
| same_time_last_week | baseline | 15.063 | 7.514 | 13.209 | 0.066 | 0.798 |
| ridge | ml | 15.143 | 10.630 | 13.279 | -0.234 | 0.796 |
| towt | baseline | 27.696 | 24.019 | 24.288 | -20.858 | 0.318 |
| time_of_week_profile | baseline | 31.367 | 28.685 | 27.507 | -25.124 | 0.125 |
| same_time_yesterday | baseline | 31.662 | 18.876 | 27.766 | 0.368 | 0.109 |
| persistence | baseline | 31.662 | 18.876 | 27.766 | 0.368 | 0.109 |
| time_of_day_profile | baseline | 31.774 | 28.700 | 27.863 | -25.132 | 0.103 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 16.781 | 20.539 |
| MAE (kWh) | 10.598 | 11.575 |
| CV(RMSE) % | 13.912 | 17.028 |
| NMBE % | -2.649 | 1.652 |
| R² | 0.818 | 0.727 |

Skill vs same_time_last_week: **0.18** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 13.9% (limit 30%), NMBE -2.6% (limit ±10%): **passes**.

90% prediction interval: ±13.8 kWh (width from validation errors); it contained 76% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.19 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.23 |
| 2017-10-19 to 2017-12-31 | 1753 | 0.21 |

Pooled skill: **0.21**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 49% |
| calendar (time of day, weekday) | 49% |
| airTemperature | 2% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
