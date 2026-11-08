# Run report: bdg2-Moose_education_Abbie

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 1690.06 for 6 d 1 h (2016-05-19 07:00:00 to 2016-05-25 08:00:00); 283 such stretch(es), 146 d 10 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 283 stuck stretch(es) set to missing. (2099)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (165)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (209)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (170)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-21 05:00:00 | 10787 |
| val | 2017-06-22 06:00:00 | 2017-09-25 12:00:00 | 2287 |
| test | 2017-09-26 13:00:00 | 2017-12-31 23:00:00 | 2289 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 73.967 | 36.393 | 6.334 | -0.599 | 0.905 |
| gbm | ml | 77.818 | 39.860 | 6.664 | -1.619 | 0.894 |
| ridge | ml | 92.876 | 57.740 | 7.954 | -2.126 | 0.850 |
| same_time_last_week | baseline | 95.144 | 36.203 | 8.148 | 0.086 | 0.842 |
| towt | baseline | 122.426 | 99.919 | 10.484 | -8.242 | 0.739 |
| time_of_week_profile | baseline | 130.319 | 109.142 | 11.160 | -9.151 | 0.704 |
| time_of_day_profile | baseline | 131.336 | 109.576 | 11.247 | -9.160 | 0.699 |
| persistence | baseline | 192.213 | 87.658 | 16.460 | -0.045 | 0.356 |
| same_time_yesterday | baseline | 192.213 | 87.658 | 16.460 | -0.045 | 0.356 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 92.681 | 116.056 |
| MAE (kWh) | 47.096 | 49.222 |
| CV(RMSE) % | 7.952 | 9.958 |
| NMBE % | -2.029 | -0.267 |
| R² | 0.859 | 0.779 |

Skill vs same_time_last_week: **0.20** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 8.0% (limit 30%), NMBE -2.0% (limit ±10%): **passes**.

90% prediction interval: ±72 kWh (width from validation errors); it contained 86% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-21 to 2017-08-24 | 1542 | 0.25 |
| 2017-08-24 to 2017-10-27 | 1541 | 0.25 |
| 2017-10-28 to 2017-12-31 | 1541 | 0.22 |

Pooled skill: **0.24**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 64% |
| calendar (time of day, weekday) | 36% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
