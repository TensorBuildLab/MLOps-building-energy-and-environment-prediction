# Run report: bdg2-Lamb_education_Sabrina

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 1.2 for 12 h (2016-08-19 23:00:00 to 2016-08-20 11:00:00); 36 such stretch(es), 11 d 15 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10 for 1 d 18 h (2017-12-20 15:00:00 to 2017-12-22 09:00:00); 278 such stretch(es), 101 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3.1 for 7 h (2017-09-15 23:00:00 to 2017-09-16 06:00:00); 4 such stretch(es), 1 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 3 single-sample spike(s), e.g. 16, 12.9, 11.8 at 2016-03-28 04:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 36 stuck stretch(es) set to missing. (96)
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
| train | 2016-01-01 00:00:00 | 2017-04-27 21:00:00 | 11386 |
| val | 2017-04-28 22:00:00 | 2017-09-19 19:00:00 | 2416 |
| test | 2017-09-20 20:00:00 | 2017-12-31 23:00:00 | 2417 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 1.095 | 0.538 | 37.048 | 0.938 | 0.879 |
| gbm_change | ml | 1.095 | 0.514 | 37.050 | 0.274 | 0.879 |
| ridge | ml | 1.796 | 1.177 | 60.755 | -0.710 | 0.675 |
| same_time_last_week | baseline | 2.079 | 0.921 | 70.335 | 0.867 | 0.565 |
| towt | baseline | 2.410 | 1.360 | 81.546 | -5.757 | 0.415 |
| time_of_day_profile | baseline | 2.483 | 1.252 | 84.012 | -16.021 | 0.379 |
| persistence | baseline | 2.485 | 0.985 | 84.076 | -0.469 | 0.378 |
| same_time_yesterday | baseline | 2.485 | 0.985 | 84.076 | -0.469 | 0.378 |
| time_of_week_profile | baseline | 2.489 | 1.254 | 84.225 | -16.104 | 0.376 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 1.099 | 2.894 |
| MAE (kWh) | 0.603 | 1.254 |
| CV(RMSE) % | 26.966 | 70.989 |
| NMBE % | -1.121 | -6.612 |
| R² | 0.941 | 0.591 |

Skill vs same_time_last_week: **0.62** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 27.0% (limit 30%), NMBE -1.1% (limit ±10%): **passes**.

90% prediction interval: ±1.33 kWh (width from validation errors); it contained 87% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-04-27 to 2017-08-15 | 1627 | 0.55 |
| 2017-08-15 to 2017-10-23 | 1627 | 0.38 |
| 2017-10-23 to 2017-12-31 | 1627 | 0.68 |

Pooled skill: **0.59**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 61% |
| calendar (time of day, weekday) | 38% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
