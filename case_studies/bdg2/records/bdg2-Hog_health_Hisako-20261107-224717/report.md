# Run report: bdg2-Hog_health_Hisako

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

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
| train | 2016-01-01 00:00:00 | 2017-05-26 17:00:00 | 12275 |
| val | 2017-05-27 18:00:00 | 2017-09-13 07:00:00 | 2606 |
| test | 2017-09-14 08:00:00 | 2017-12-31 23:00:00 | 2607 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 10.489 | 6.660 | 5.156 | -1.220 | 0.858 |
| gbm | ml | 10.564 | 6.877 | 5.193 | -1.441 | 0.856 |
| time_of_week_profile | baseline | 11.231 | 7.652 | 5.521 | -2.633 | 0.838 |
| time_of_day_profile | baseline | 11.479 | 7.884 | 5.643 | -2.642 | 0.830 |
| ridge | ml | 11.554 | 7.791 | 5.680 | -0.531 | 0.828 |
| towt | baseline | 12.889 | 9.593 | 6.336 | -4.101 | 0.786 |
| same_time_last_week | baseline | 13.465 | 8.318 | 6.619 | -0.110 | 0.766 |
| persistence | baseline | 20.939 | 12.563 | 10.293 | 0.083 | 0.435 |
| same_time_yesterday | baseline | 20.939 | 12.563 | 10.293 | 0.083 | 0.435 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 9.977 | 15.502 |
| MAE (kWh) | 6.452 | 11.947 |
| CV(RMSE) % | 5.078 | 7.890 |
| NMBE % | -1.777 | -5.803 |
| R² | 0.861 | 0.665 |

Skill vs time_of_week_profile: **0.36** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 5.1% (limit 30%), NMBE -1.8% (limit ±10%): **passes**.

90% prediction interval: ±13.4 kWh (width from validation errors); it contained 90% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.04 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.14 |
| 2017-10-19 to 2017-12-31 | 1753 | 0.37 |

Pooled skill: **0.24**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 66% |
| calendar (time of day, weekday) | 34% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
