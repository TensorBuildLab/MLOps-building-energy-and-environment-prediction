# Run report: bdg2-Robin_education_Madeline

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 362.616 for 44 d 10 h (2016-03-08 13:00:00 to 2016-04-21 23:00:00); 24 such stretch(es), 104 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 24 stuck stretch(es) set to missing. (2382)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-12 17:00:00 | 10613 |
| val | 2017-06-13 18:00:00 | 2017-09-17 16:00:00 | 2250 |
| test | 2017-09-18 17:00:00 | 2017-12-31 23:00:00 | 2251 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 12.135 | 8.476 | 3.321 | 0.010 | 0.919 |
| towt | baseline | 12.466 | 8.841 | 3.412 | 0.850 | 0.914 |
| gbm_change | ml | 12.925 | 8.827 | 3.537 | 0.081 | 0.908 |
| time_of_week_profile | baseline | 13.749 | 9.498 | 3.763 | 0.721 | 0.896 |
| time_of_day_profile | baseline | 14.254 | 9.959 | 3.901 | 0.754 | 0.888 |
| ridge | ml | 15.685 | 12.041 | 4.293 | -0.160 | 0.864 |
| same_time_last_week | baseline | 18.893 | 13.116 | 5.170 | 0.163 | 0.803 |
| persistence | baseline | 27.951 | 17.304 | 7.649 | -0.050 | 0.569 |
| same_time_yesterday | baseline | 27.951 | 17.304 | 7.649 | -0.050 | 0.569 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 15.002 | 24.048 |
| MAE (kWh) | 9.237 | 13.146 |
| CV(RMSE) % | 4.263 | 6.834 |
| NMBE % | -1.336 | -2.915 |
| R² | 0.877 | 0.683 |

Skill vs towt: **0.38** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 4.3% (limit 30%), NMBE -1.3% (limit ±10%): **passes**.

90% prediction interval: ±18.7 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-12 to 2017-08-17 | 1517 | 0.02 |
| 2017-08-17 to 2017-10-19 | 1516 | 0.11 |
| 2017-10-19 to 2017-12-31 | 1516 | 0.39 |

Pooled skill: **0.27**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 64% |
| calendar (time of day, weekday) | 36% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
