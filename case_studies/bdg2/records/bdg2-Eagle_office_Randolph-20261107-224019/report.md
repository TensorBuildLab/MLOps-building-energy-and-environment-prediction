# Run report: bdg2-Eagle_office_Randolph

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 73.74 for 3 d 6 h (2016-07-16 04:00:00 to 2016-07-19 10:00:00); 4 such stretch(es), 4 d 12 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 4 stuck stretch(es) set to missing. (88)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-28 12:00:00 | 12159 |
| val | 2017-05-29 13:00:00 | 2017-09-14 08:00:00 | 2581 |
| test | 2017-09-15 09:00:00 | 2017-12-31 23:00:00 | 2582 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 14.094 | 8.488 | 13.157 | 1.535 | 0.839 |
| gbm_change | ml | 14.269 | 8.788 | 13.320 | 1.060 | 0.835 |
| ridge | ml | 16.196 | 11.360 | 15.119 | 0.515 | 0.787 |
| time_of_week_profile | baseline | 16.321 | 10.440 | 15.236 | -3.449 | 0.784 |
| towt | baseline | 16.354 | 10.322 | 15.266 | -0.338 | 0.783 |
| time_of_day_profile | baseline | 16.670 | 10.787 | 15.562 | -3.401 | 0.774 |
| same_time_last_week | baseline | 19.267 | 11.843 | 17.986 | -0.226 | 0.698 |
| persistence | baseline | 25.371 | 15.538 | 23.684 | 0.277 | 0.477 |
| same_time_yesterday | baseline | 25.371 | 15.538 | 23.684 | 0.277 | 0.477 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 18.622 | 20.226 |
| MAE (kWh) | 11.801 | 12.927 |
| CV(RMSE) % | 16.651 | 18.086 |
| NMBE % | 3.913 | 1.795 |
| R² | 0.729 | 0.680 |

Skill vs time_of_week_profile: **0.08** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 16.7% (limit 30%), NMBE 3.9% (limit ±10%): **passes**.

90% prediction interval: ±23.3 kWh (width from validation errors); it contained 84% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-28 to 2017-08-08 | 1737 | 0.05 |
| 2017-08-09 to 2017-10-20 | 1737 | 0.16 |
| 2017-10-20 to 2017-12-31 | 1737 | 0.06 |

Pooled skill: **0.10**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 60% |
| calendar (time of day, weekday) | 39% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
