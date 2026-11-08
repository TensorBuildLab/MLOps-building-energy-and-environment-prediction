# Run report: bdg2-Lamb_education_Maritza

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 4.2 for 6 h (2016-07-16 13:00:00 to 2016-07-16 19:00:00); 3 such stretch(es), 18 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10 for 1 d 18 h (2017-12-20 15:00:00 to 2017-12-22 09:00:00); 278 such stretch(es), 101 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3.1 for 7 h (2017-09-15 23:00:00 to 2017-09-16 06:00:00); 4 such stretch(es), 1 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 3 single-sample spike(s), e.g. 16, 12.9, 11.8 at 2016-03-28 04:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 3 stuck stretch(es) set to missing. (3)
- mask_stuck `airTemperature`: 278 stuck stretch(es) set to missing. (1035)
- mask_stuck `windSpeed`: 4 stuck stretch(es) set to missing. (5)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (299)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (24)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (31)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-04-27 10:00:00 | 11509 |
| val | 2017-04-28 11:00:00 | 2017-09-20 03:00:00 | 2442 |
| test | 2017-09-21 04:00:00 | 2017-12-31 23:00:00 | 2443 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 1.312 | 0.742 | 22.673 | -1.948 | 0.832 |
| gbm_change | ml | 1.359 | 0.735 | 23.482 | -2.197 | 0.820 |
| ridge | ml | 1.802 | 1.258 | 31.141 | -0.284 | 0.684 |
| same_time_last_week | baseline | 2.088 | 0.976 | 36.087 | 1.140 | 0.575 |
| time_of_day_profile | baseline | 2.388 | 1.446 | 41.275 | -4.992 | 0.444 |
| time_of_week_profile | baseline | 2.401 | 1.451 | 41.500 | -5.062 | 0.438 |
| towt | baseline | 2.404 | 1.495 | 41.543 | -3.403 | 0.437 |
| persistence | baseline | 2.527 | 1.104 | 43.672 | -0.073 | 0.378 |
| same_time_yesterday | baseline | 2.527 | 1.104 | 43.672 | -0.073 | 0.378 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 1.355 | 3.339 |
| MAE (kWh) | 0.689 | 1.397 |
| CV(RMSE) % | 20.424 | 50.331 |
| NMBE % | -1.285 | -6.931 |
| R² | 0.926 | 0.551 |

Skill vs same_time_last_week: **0.59** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 20.4% (limit 30%), NMBE -1.3% (limit ±10%): **passes**.

90% prediction interval: ±1.89 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-04-27 to 2017-08-15 | 1645 | 0.42 |
| 2017-08-15 to 2017-10-24 | 1644 | 0.33 |
| 2017-10-24 to 2017-12-31 | 1644 | 0.62 |

Pooled skill: **0.54**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 65% |
| calendar (time of day, weekday) | 35% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
