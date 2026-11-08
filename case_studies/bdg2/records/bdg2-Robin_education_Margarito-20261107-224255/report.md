# Run report: bdg2-Robin_education_Margarito

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 498.293 for 43 d 10 h (2016-03-08 13:00:00 to 2016-04-20 23:00:00); 7 such stretch(es), 72 d 11 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 7 stuck stretch(es) set to missing. (1704)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-16 23:00:00 | 11088 |
| val | 2017-06-18 00:00:00 | 2017-09-23 23:00:00 | 2352 |
| test | 2017-09-25 00:00:00 | 2017-12-31 23:00:00 | 2352 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| towt | baseline | 37.339 | 29.073 | 6.601 | -1.931 | 0.776 |
| ridge | ml | 38.989 | 30.098 | 6.893 | -1.105 | 0.756 |
| gbm_change | ml | 39.675 | 30.581 | 7.014 | -1.525 | 0.747 |
| gbm | ml | 41.899 | 32.642 | 7.408 | -2.335 | 0.718 |
| same_time_yesterday | baseline | 51.113 | 37.759 | 9.037 | -0.158 | 0.581 |
| persistence | baseline | 51.113 | 37.759 | 9.037 | -0.158 | 0.581 |
| time_of_day_profile | baseline | 61.500 | 44.803 | 10.873 | 5.957 | 0.393 |
| time_of_week_profile | baseline | 61.569 | 45.014 | 10.885 | 5.950 | 0.392 |
| same_time_last_week | baseline | 63.157 | 47.503 | 11.166 | -0.904 | 0.360 |

## Test result

Chosen model: **towt** 

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 49.840 | 49.840 |
| MAE (kWh) | 41.029 | 41.029 |
| CV(RMSE) % | 10.325 | 10.325 |
| NMBE % | -7.306 | -7.306 |
| R² | 0.386 | 0.386 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 10.3% (limit 30%), NMBE -7.3% (limit ±10%): **passes**.

90% prediction interval: ±59 kWh (width from validation errors); it contained 82% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-17 to 2017-08-21 | 1584 | 0.00 |
| 2017-08-22 to 2017-10-26 | 1584 | 0.00 |
| 2017-10-27 to 2017-12-31 | 1584 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| airTemperature | 100% |

> Warning: No machine-learning model beat the 'towt' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
