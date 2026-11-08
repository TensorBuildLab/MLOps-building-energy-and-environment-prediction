# Run report: bdg2-Eagle_office_Freida

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 50 for 8 d 18 h (2017-12-22 22:00:00 to 2017-12-31 16:00:00); 8 such stretch(es), 14 d 3 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 8 stuck stretch(es) set to missing. (299)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-23 10:00:00 | 11940 |
| val | 2017-05-24 11:00:00 | 2017-09-07 09:00:00 | 2534 |
| test | 2017-09-08 10:00:00 | 2017-12-23 03:00:00 | 2536 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 4.155 | 3.090 | 8.854 | -0.891 | 0.869 |
| gbm | ml | 4.249 | 3.158 | 9.056 | -0.519 | 0.863 |
| ridge | ml | 4.679 | 3.602 | 9.972 | 0.372 | 0.834 |
| same_time_last_week | baseline | 5.144 | 3.658 | 10.963 | 0.433 | 0.800 |
| same_time_yesterday | baseline | 6.650 | 4.517 | 14.171 | 0.083 | 0.666 |
| persistence | baseline | 6.650 | 4.517 | 14.171 | 0.083 | 0.666 |
| towt | baseline | 19.784 | 18.164 | 42.163 | -38.669 | -1.960 |
| time_of_day_profile | baseline | 20.501 | 18.971 | 43.690 | -40.409 | -2.179 |
| time_of_week_profile | baseline | 20.503 | 18.982 | 43.696 | -40.440 | -2.179 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 6.029 | 7.977 |
| MAE (kWh) | 4.083 | 5.395 |
| CV(RMSE) % | 11.721 | 15.508 |
| NMBE % | -0.573 | 0.158 |
| R² | 0.825 | 0.693 |

Skill vs same_time_last_week: **0.24** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.7% (limit 30%), NMBE -0.6% (limit ±10%): **passes**.

90% prediction interval: ±6.82 kWh (width from validation errors); it contained 83% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-23 to 2017-08-02 | 1706 | 0.18 |
| 2017-08-02 to 2017-10-13 | 1706 | 0.18 |
| 2017-10-13 to 2017-12-23 | 1706 | 0.27 |

Pooled skill: **0.23**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 80% |
| calendar (time of day, weekday) | 20% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
