# Run report: bdg2-Moose_education_Gladys

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 935.012 for 17 h (2016-08-07 05:00:00 to 2016-08-07 22:00:00); 224 such stretch(es), 83 d 15 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 224 stuck stretch(es) set to missing. (887)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (165)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (209)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (170)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-03 22:00:00 | 11596 |
| val | 2017-06-04 23:00:00 | 2017-09-15 10:00:00 | 2460 |
| test | 2017-09-16 11:00:00 | 2017-12-31 23:00:00 | 2462 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 90.069 | 42.722 | 8.301 | -1.057 | 0.902 |
| ridge | ml | 100.650 | 59.305 | 9.276 | -0.756 | 0.878 |
| gbm_change | ml | 102.585 | 45.700 | 9.454 | -0.543 | 0.873 |
| towt | baseline | 102.898 | 67.202 | 9.483 | -3.308 | 0.872 |
| time_of_week_profile | baseline | 108.443 | 74.879 | 9.994 | -4.996 | 0.858 |
| same_time_last_week | baseline | 110.527 | 42.872 | 10.186 | 0.437 | 0.853 |
| time_of_day_profile | baseline | 117.881 | 79.421 | 10.864 | -4.974 | 0.832 |
| persistence | baseline | 231.900 | 125.901 | 21.372 | 0.504 | 0.352 |
| same_time_yesterday | baseline | 231.900 | 125.901 | 21.372 | 0.504 | 0.352 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 84.981 | 120.030 |
| MAE (kWh) | 54.898 | 87.393 |
| CV(RMSE) % | 7.950 | 11.229 |
| NMBE % | -1.176 | -5.607 |
| R² | 0.914 | 0.828 |

Skill vs towt: **0.29** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 7.9% (limit 30%), NMBE -1.2% (limit ±10%): **passes**.

90% prediction interval: ±70.8 kWh (width from validation errors); it contained 76% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-03 to 2017-08-11 | 1657 | 0.16 |
| 2017-08-12 to 2017-10-23 | 1657 | 0.21 |
| 2017-10-23 to 2017-12-31 | 1656 | 0.27 |

Pooled skill: **0.22**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 71% |
| calendar (time of day, weekday) | 28% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
