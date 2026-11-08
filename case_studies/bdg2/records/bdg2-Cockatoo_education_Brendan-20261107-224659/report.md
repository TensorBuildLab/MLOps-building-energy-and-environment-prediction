# Run report: bdg2-Cockatoo_education_Brendan

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
| train | 2016-01-01 00:00:00 | 2017-06-10 00:00:00 | 11279 |
| val | 2017-06-11 01:00:00 | 2017-09-21 20:00:00 | 2393 |
| test | 2017-09-22 21:00:00 | 2017-12-31 23:00:00 | 2394 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 4.764 | 3.847 | 7.451 | -4.102 | 0.788 |
| ridge | ml | 4.767 | 3.762 | 7.455 | -0.078 | 0.788 |
| gbm_change | ml | 4.842 | 3.891 | 7.572 | -3.477 | 0.781 |
| same_time_last_week | baseline | 5.460 | 4.197 | 8.538 | -0.314 | 0.722 |
| same_time_yesterday | baseline | 7.507 | 5.369 | 11.740 | -0.032 | 0.475 |
| persistence | baseline | 7.507 | 5.369 | 11.740 | -0.032 | 0.475 |
| time_of_week_profile | baseline | 8.155 | 7.250 | 12.754 | -11.166 | 0.380 |
| time_of_day_profile | baseline | 8.177 | 7.255 | 12.788 | -11.158 | 0.377 |
| towt | baseline | 8.814 | 7.924 | 13.784 | -12.273 | 0.276 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 4.167 | 6.660 |
| MAE (kWh) | 3.179 | 4.888 |
| CV(RMSE) % | 6.010 | 9.606 |
| NMBE % | 0.056 | -0.750 |
| R² | 0.871 | 0.669 |

Skill vs same_time_last_week: **0.37** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 6.0% (limit 30%), NMBE 0.1% (limit ±10%): **passes**.

90% prediction interval: ±7.6 kWh (width from validation errors); it contained 93% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-10 to 2017-08-19 | 1612 | 0.12 |
| 2017-08-19 to 2017-10-25 | 1612 | 0.27 |
| 2017-10-25 to 2017-12-31 | 1611 | 0.39 |

Pooled skill: **0.28**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 70% |
| calendar (time of day, weekday) | 30% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
