# Run report: bdg2-Hog_office_Rolando

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 433 for 3 d (2016-11-06 11:00:00 to 2016-11-09 11:00:00); 4 such stretch(es), 3 d 18 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 4 stuck stretch(es) set to missing. (70)
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
| train | 2016-01-01 00:00:00 | 2017-05-27 13:00:00 | 12231 |
| val | 2017-05-28 14:00:00 | 2017-09-13 17:00:00 | 2596 |
| test | 2017-09-14 18:00:00 | 2017-12-31 23:00:00 | 2598 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 13.434 | 10.029 | 3.133 | -0.097 | 0.838 |
| ridge | ml | 13.685 | 10.312 | 3.191 | -0.473 | 0.832 |
| gbm | ml | 15.992 | 12.564 | 3.729 | -0.885 | 0.771 |
| same_time_last_week | baseline | 16.037 | 11.979 | 3.739 | -0.513 | 0.770 |
| same_time_yesterday | baseline | 19.047 | 13.035 | 4.441 | 0.019 | 0.675 |
| persistence | baseline | 19.047 | 13.035 | 4.441 | 0.019 | 0.675 |
| time_of_day_profile | baseline | 171.138 | 169.623 | 39.906 | 39.561 | -25.222 |
| time_of_week_profile | baseline | 171.189 | 169.710 | 39.918 | 39.581 | -25.238 |
| towt | baseline | 276.385 | 270.880 | 64.448 | 63.177 | -67.392 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 7, 'base__max_iter': 100, 'base__learning_rate': 0.2, 'base__l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 26.734 | 17.868 |
| MAE (kWh) | 14.640 | 9.510 |
| CV(RMSE) % | 6.302 | 4.212 |
| NMBE % | -2.642 | -0.258 |
| R² | -0.035 | 0.538 |

Skill vs same_time_last_week: **-0.50** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 6.3% (limit 30%), NMBE -2.6% (limit ±10%): **passes**.

90% prediction interval: ±22.1 kWh (width from validation errors); it contained 83% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-08 | 1748 | 0.25 |
| 2017-08-08 to 2017-10-20 | 1747 | -0.25 |
| 2017-10-20 to 2017-12-31 | 1747 | -0.65 |

Pooled skill: **-0.34**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 50% |
| calendar (time of day, weekday) | 33% |
| dewTemperature | 15% |
| airTemperature | 1% |

> Warning: The model is barely better than same_time_last_week on test data (skill -0.50).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
