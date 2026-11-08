# Run report: bdg2-Hog_office_Thomas

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 4 for 13 h (2017-06-24 07:00:00 to 2017-06-24 20:00:00); 14 such stretch(es), 4 d 15 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 14 stuck stretch(es) set to missing. (41)
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
| train | 2016-01-01 00:00:00 | 2017-04-29 09:00:00 | 11560 |
| val | 2017-04-30 10:00:00 | 2017-08-13 13:00:00 | 2453 |
| test | 2017-08-14 14:00:00 | 2017-11-29 09:00:00 | 2455 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 14.729 | 6.578 | 112.349 | -6.875 | 0.650 |
| ridge | ml | 16.788 | 9.796 | 128.050 | 10.930 | 0.546 |
| gbm_change | ml | 17.487 | 7.923 | 133.383 | -15.953 | 0.507 |
| same_time_last_week | baseline | 20.151 | 7.597 | 153.701 | -12.374 | 0.345 |
| same_time_yesterday | baseline | 22.879 | 8.642 | 174.511 | -8.421 | 0.156 |
| persistence | baseline | 22.879 | 8.642 | 174.511 | -8.421 | 0.156 |
| towt | baseline | 37.652 | 29.835 | 287.193 | -83.618 | -1.286 |
| time_of_day_profile | baseline | 60.013 | 53.887 | 457.759 | -399.360 | -4.808 |
| time_of_week_profile | baseline | 60.663 | 54.110 | 462.711 | -399.270 | -4.934 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 27.024 | 27.558 |
| MAE (kWh) | 18.530 | 11.825 |
| CV(RMSE) % | 110.996 | 113.189 |
| NMBE % | -32.528 | -7.327 |
| R² | 0.528 | 0.510 |

Skill vs same_time_last_week: **0.02** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 111.0% (limit 30%), NMBE -32.5% (limit ±10%): **does not pass**.

90% prediction interval: ±20.7 kWh (width from validation errors); it contained 61% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-04-29 to 2017-07-08 | 1652 | 0.29 |
| 2017-07-08 to 2017-09-18 | 1652 | 0.23 |
| 2017-09-18 to 2017-11-29 | 1651 | -0.06 |

Pooled skill: **0.09**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 80% |
| calendar (time of day, weekday) | 19% |
| windSpeed | 1% |

> Warning: The model is barely better than same_time_last_week on test data (skill 0.02).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
