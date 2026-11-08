# Run report: bdg2-Bull_education_Sebastian

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 27 for 11 h (2016-12-29 07:00:00 to 2016-12-29 18:00:00); 38 such stretch(es), 10 d 22 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 38 stuck stretch(es) set to missing. (72)
- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-27 05:00:00 | 12000 |
| val | 2017-05-28 06:00:00 | 2017-09-11 15:00:00 | 2547 |
| test | 2017-09-12 16:00:00 | 2017-12-31 23:00:00 | 2549 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 3.346 | 2.342 | 8.971 | 0.738 | 0.903 |
| gbm_change | ml | 3.676 | 2.405 | 9.855 | 1.146 | 0.883 |
| ridge | ml | 3.990 | 2.880 | 10.698 | 1.285 | 0.862 |
| time_of_week_profile | baseline | 4.569 | 3.252 | 12.250 | -2.788 | 0.819 |
| same_time_last_week | baseline | 4.593 | 3.126 | 12.316 | 1.784 | 0.817 |
| time_of_day_profile | baseline | 4.625 | 3.333 | 12.399 | -2.778 | 0.815 |
| towt | baseline | 4.627 | 3.317 | 12.407 | -1.144 | 0.814 |
| persistence | baseline | 7.202 | 4.508 | 19.309 | 0.515 | 0.551 |
| same_time_yesterday | baseline | 7.202 | 4.508 | 19.309 | 0.515 | 0.551 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 4.676 | 7.104 |
| MAE (kWh) | 2.403 | 4.639 |
| CV(RMSE) % | 11.653 | 17.703 |
| NMBE % | -0.147 | 4.456 |
| R² | 0.880 | 0.724 |

Skill vs time_of_week_profile: **0.34** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.7% (limit 30%), NMBE -0.1% (limit ±10%): **passes**.

90% prediction interval: ±5.08 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-06 | 1715 | 0.32 |
| 2017-08-06 to 2017-10-17 | 1715 | 0.34 |
| 2017-10-17 to 2017-12-31 | 1714 | 0.30 |

Pooled skill: **0.31**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 71% |
| calendar (time of day, weekday) | 29% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
