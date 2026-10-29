# Run report: co2_forecast_1h_roomB

**Task:** forecast co2 (co2, ppm) 1 h ahead (4 step(s) of 15 min)

## Data check

26916 raw rows from 2023-02-27 00:00:00 to 2023-05-31 23:55:00, typical step 5 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| warning | `index:gaps` | 2 gap(s) longer than 3 time steps, 13 h 10 min in total; longest 12 h 5 min from 2023-04-02 07:40:00 to 2023-04-02 19:45:00. | Gaps stay missing. Short gaps in inputs are forward-filled; the target is never filled. |
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| info | `columns:undeclared` | 12 column(s) are not declared and will be ignored: wind, sol_e, sol_s, sol_w, vent_el, sat, dh, hc .... | Declare any you want the model to use. |
| warning | `spikes:co2` | 2 single-sample spike(s), e.g. 1521, 504 at 2023-04-21 16:10:00. | prepare() treats them as missing. |
| warning | `stuck:oat` | Sensor repeats exactly 7.16995 for 9 h 30 min (2023-03-21 21:15:00 to 2023-03-22 06:45:00); 6 such stretch(es), 1 d 22 h in total. | prepare() treats these stretches as missing. |
| warning | `spikes:rt` | 15 single-sample spike(s), e.g. 23.27, 23.45, 23.43 at 2023-03-05 12:50:00. | prepare() treats them as missing. |
| warning | `stuck:sol` | Sensor repeats exactly 3.9753 for 12 h 50 min (2023-03-06 18:05:00 to 2023-03-07 06:55:00); 87 such stretch(es), 33 d 14 h in total. | prepare() treats these stretches as missing. |

**Decisions recorded:**

- co2 is change-of-value logged (deadband ~50 ppm): flat stretches are normal, declared flat_ok. Room temperature switched to degF on 2023-05-12 10:00; converted per sample (>45 -> degF) before bemlops. Duplicate day (2023-05-25) and a reversed block (2023-04-24) removed in the loader. -999 CO2 and outdoor temperature spikes masked.

## Preparation

- mask_spikes `co2`: Single-sample spikes set to missing. (2)
- mask_stuck `oat`: 6 stuck stretch(es) set to missing. (557)
- mask_spikes `rt`: Single-sample spikes set to missing. (15)
- convert_units `flow`: Converted m3/h to m3/s.
- mask_stuck `sol`: 87 stuck stretch(es) set to missing. (9759)
- resample: Resampled to a regular 15 min grid (9024 rows). (9024)
- forward_fill `oat`: Filled input gaps up to 1h with the last known value. (34)
- forward_fill `rt`: Filled input gaps up to 1h with the last known value. (9)
- forward_fill `active`: Filled input gaps up to 1h with the last known value. (9)
- forward_fill `light`: Filled input gaps up to 1h with the last known value. (10)
- forward_fill `flow`: Filled input gaps up to 1h with the last known value. (9)
- forward_fill `damper`: Filled input gaps up to 1h with the last known value. (10)
- forward_fill `sol`: Filled input gaps up to 1h with the last known value. (353)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2023-02-27 01:00:00 | 2023-05-03 23:00:00 | 6276 |
| val | 2023-05-04 00:15:00 | 2023-05-17 23:15:00 | 1340 |
| test | 2023-05-18 00:30:00 | 2023-05-31 23:45:00 | 1342 |

Time-ordered, with a 1 h gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 26.269 | 11.970 | 5.574 | 0.001 | 0.803 |
| ridge | ml | 26.556 | 17.253 | 5.635 | -0.560 | 0.799 |
| gbm | ml | 29.694 | 20.732 | 6.301 | -3.273 | 0.749 |
| same_time_yesterday | baseline | 63.966 | 46.307 | 13.573 | -0.773 | -0.166 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (ppm) | 29.470 | 29.470 |
| MAE (ppm) | 12.448 | 12.448 |
| CV(RMSE) % | 6.333 | 6.333 |
| NMBE % | -0.010 | -0.010 |
| R² | 0.736 | 0.736 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

> Warning: No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
