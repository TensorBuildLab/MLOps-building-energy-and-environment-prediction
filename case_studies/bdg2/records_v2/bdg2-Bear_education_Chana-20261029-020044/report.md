# Run report: bdg2-Bear_education_Chana

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 17 for 21 h (2016-03-19 16:00:00 to 2016-03-20 13:00:00); 241 such stretch(es), 80 d 9 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 14.4 for 11 h (2016-08-05 21:00:00 to 2016-08-06 08:00:00); 52 such stretch(es), 15 d 1 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-09-24 01:00:00 to 2017-09-24 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing. |
| warning | `spikes:windSpeed` | 1 single-sample spike(s), e.g. 16.5 at 2017-02-20 20:00:00. | prepare() treats them as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 241 stuck stretch(es) set to missing. (724)
- mask_stuck `airTemperature`: 52 stuck stretch(es) set to missing. (101)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (54)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (4)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-22 17:00:00 | 11746 |
| val | 2017-05-23 18:00:00 | 2017-09-09 01:00:00 | 2493 |
| test | 2017-09-10 02:00:00 | 2017-12-31 23:00:00 | 2497 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 2.000 | 1.332 | 10.027 | -0.413 | 0.737 |
| gbm_change | ml | 2.140 | 1.430 | 10.726 | -1.118 | 0.699 |
| ridge | ml | 2.316 | 1.664 | 11.611 | 0.146 | 0.647 |
| time_of_day_profile | baseline | 3.188 | 2.275 | 15.981 | -8.995 | 0.332 |
| persistence | baseline | 3.237 | 2.098 | 16.226 | -0.486 | 0.311 |
| same_time_yesterday | baseline | 3.237 | 2.098 | 16.226 | -0.486 | 0.311 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 2.210 | 3.665 |
| MAE (kWh) | 1.498 | 2.578 |
| CV(RMSE) % | 9.834 | 16.314 |
| NMBE % | 0.699 | 4.625 |
| R² | 0.853 | 0.596 |

Skill vs time_of_day_profile: **0.40** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 9.8% (limit 30%), NMBE 0.7% (limit ±10%): **passes**.

90% prediction interval: ±3.33 kWh (width from validation errors); it contained 88% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-22 to 2017-08-03 | 1679 | 0.46 |
| 2017-08-03 to 2017-10-15 | 1678 | 0.28 |
| 2017-10-15 to 2017-12-31 | 1678 | 0.39 |

Pooled skill: **0.38**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 61% |
| calendar (time of day, weekday) | 39% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
