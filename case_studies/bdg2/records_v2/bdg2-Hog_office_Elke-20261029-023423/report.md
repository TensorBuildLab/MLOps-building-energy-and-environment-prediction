# Run report: bdg2-Hog_office_Elke

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 38 for 9 h (2017-08-26 10:00:00 to 2017-08-26 19:00:00); 5 such stretch(es), 1 d 12 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing. |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 5 stuck stretch(es) set to missing. (11)
- mask_stuck `airTemperature`: 58 stuck stretch(es) set to missing. (149)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (62)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (11)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 05:00:00 | 12264 |
| val | 2017-05-27 06:00:00 | 2017-09-13 07:00:00 | 2604 |
| test | 2017-09-14 08:00:00 | 2017-12-31 23:00:00 | 2605 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 8.962 | 6.112 | 14.524 | -1.138 | 0.910 |
| ridge | ml | 9.652 | 6.475 | 15.641 | 0.065 | 0.896 |
| gbm | ml | 10.115 | 6.744 | 16.392 | -0.273 | 0.885 |
| time_of_day_profile | baseline | 11.361 | 8.398 | 18.411 | -6.703 | 0.855 |
| persistence | baseline | 24.265 | 13.564 | 39.324 | 0.178 | 0.340 |
| same_time_yesterday | baseline | 24.265 | 13.564 | 39.324 | 0.178 | 0.340 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 5.929 | 11.990 |
| MAE (kWh) | 3.994 | 8.068 |
| CV(RMSE) % | 9.472 | 19.155 |
| NMBE % | -1.594 | -3.980 |
| R² | 0.954 | 0.813 |

Skill vs time_of_day_profile: **0.51** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 9.5% (limit 30%), NMBE -1.6% (limit ±10%): **passes**.

90% prediction interval: ±12.5 kWh (width from validation errors); it contained 97% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1753 | 0.17 |
| 2017-08-07 to 2017-10-19 | 1752 | 0.43 |
| 2017-10-19 to 2017-12-31 | 1752 | 0.49 |

Pooled skill: **0.37**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 61% |
| calendar (time of day, weekday) | 39% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
