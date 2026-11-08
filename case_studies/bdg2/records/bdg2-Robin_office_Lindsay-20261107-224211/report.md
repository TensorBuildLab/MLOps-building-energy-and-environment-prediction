# Run report: bdg2-Robin_office_Lindsay

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 63.0022 for 9 d 6 h (2017-12-11 17:00:00 to 2017-12-20 23:00:00); 19 such stretch(es), 39 d 22 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 19 stuck stretch(es) set to missing. (863)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-24 16:00:00 | 11676 |
| val | 2017-05-25 17:00:00 | 2017-09-07 10:00:00 | 2478 |
| test | 2017-09-08 11:00:00 | 2017-12-31 23:00:00 | 2479 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 6.053 | 4.498 | 10.431 | -4.016 | 0.783 |
| gbm_change | ml | 6.317 | 4.406 | 10.886 | -2.273 | 0.764 |
| ridge | ml | 6.551 | 4.686 | 11.290 | 0.116 | 0.746 |
| same_time_last_week | baseline | 7.631 | 5.118 | 13.150 | 0.098 | 0.655 |
| same_time_yesterday | baseline | 10.397 | 6.627 | 17.917 | 0.299 | 0.360 |
| persistence | baseline | 10.397 | 6.627 | 17.917 | 0.299 | 0.360 |
| time_of_day_profile | baseline | 20.559 | 19.536 | 35.429 | 33.660 | -1.503 |
| time_of_week_profile | baseline | 20.595 | 19.573 | 35.491 | 33.713 | -1.512 |
| towt | baseline | 49.755 | 47.349 | 85.743 | 81.613 | -13.662 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 9.119 | 7.270 |
| MAE (kWh) | 7.239 | 5.205 |
| CV(RMSE) % | 15.298 | 12.197 |
| NMBE % | -9.545 | 2.781 |
| R² | 0.651 | 0.778 |

Skill vs same_time_last_week: **-0.25** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 15.3% (limit 30%), NMBE -9.5% (limit ±10%): **passes**.

90% prediction interval: ±9.33 kWh (width from validation errors); it contained 69% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-24 to 2017-08-03 | 1669 | 0.32 |
| 2017-08-03 to 2017-10-12 | 1668 | -0.66 |
| 2017-10-13 to 2017-12-31 | 1668 | 0.18 |

Pooled skill: **-0.07**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 58% |
| calendar (time of day, weekday) | 39% |
| dewTemperature | 3% |

> Warning: The model is barely better than same_time_last_week on test data (skill -0.25).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
