# Run report: bdg2-Robin_office_Zelma

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 135.055 for 43 d 10 h (2016-03-08 13:00:00 to 2016-04-20 23:00:00); 8 such stretch(es), 73 d 9 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 8 stuck stretch(es) set to missing. (1721)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-17 04:00:00 | 11076 |
| val | 2017-06-18 05:00:00 | 2017-09-24 01:00:00 | 2349 |
| test | 2017-09-25 02:00:00 | 2017-12-31 23:00:00 | 2350 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 7.908 | 5.462 | 8.576 | -1.826 | 0.915 |
| gbm | ml | 8.061 | 5.720 | 8.742 | -1.871 | 0.912 |
| ridge | ml | 8.442 | 6.417 | 9.154 | -0.318 | 0.904 |
| same_time_last_week | baseline | 9.509 | 6.921 | 10.311 | -1.143 | 0.878 |
| same_time_yesterday | baseline | 15.652 | 9.104 | 16.973 | -0.265 | 0.668 |
| persistence | baseline | 15.652 | 9.104 | 16.973 | -0.265 | 0.668 |
| time_of_week_profile | baseline | 23.824 | 21.681 | 25.834 | -23.105 | 0.232 |
| time_of_day_profile | baseline | 23.840 | 21.652 | 25.852 | -23.090 | 0.231 |
| towt | baseline | 27.664 | 25.672 | 29.999 | -27.521 | -0.036 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 6.854 | 13.216 |
| MAE (kWh) | 4.734 | 7.644 |
| CV(RMSE) % | 7.201 | 13.886 |
| NMBE % | -0.096 | -2.397 |
| R² | 0.959 | 0.849 |

Skill vs same_time_last_week: **0.48** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 7.2% (limit 30%), NMBE -0.1% (limit ±10%): **passes**.

90% prediction interval: ±12.8 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-17 to 2017-08-22 | 1583 | 0.25 |
| 2017-08-22 to 2017-10-27 | 1582 | 0.07 |
| 2017-10-27 to 2017-12-31 | 1582 | 0.60 |

Pooled skill: **0.38**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 72% |
| calendar (time of day, weekday) | 28% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
