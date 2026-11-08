# Run report: robod-room3-plug_load_energy-1h

**Task:** forecast plug_load_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)

## Data check

8352 raw rows from 2021-09-07 00:00:00+08:00 to 2021-12-23 23:55:00+08:00, typical step 5 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| warning | `index:gaps` | 7 gap(s) longer than 3 time steps, 79 d 35 min in total; longest 68 d 5 min from 2021-10-01 23:55:00+08:00 to 2021-12-09 00:00:00+08:00. | Gaps stay missing. Short gaps in inputs are forward-filled; the target is never filled. |
| info | `columns:undeclared` | 14 column(s) are not declared and will be ignored: ceiling_fan_energy, ahu_fan_energy, cooling_coil_valve_position, cooling_coil_valve_command, ahu_fan_speed, offcoil_air_temp, offcoil_temp_setpoint, pressure_across_filter .... | Declare any you want the model to use. |
| warning | `spikes:air_temperature` | 1 single-sample spike(s), e.g. 26.852 at 2021-09-10 02:15:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:indoor_relative_humidity` | 53 single-sample spike(s), e.g. 69.088, 67.0573, 65.3896 at 2021-09-07 00:15:00+08:00. | prepare() treats them as missing. |
| warning | `stuck:occupant_count` | Sensor repeats exactly 3 for 6 h 5 min (2021-12-16 12:00:00+08:00 to 2021-12-16 18:05:00+08:00); 1 such stretch(es), 6 h 5 min in total. The value is unchanged in 89% of steps and changes by at least ~1 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `spikes:dry_bulb_temp` | 11 single-sample spike(s), e.g. 24.6033, 26.9033, 26.0046 at 2021-09-10 05:00:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:outdoor_relative_humidity` | 32 single-sample spike(s), e.g. 83.6001, 84.2, 78.985 at 2021-09-07 07:15:00+08:00. | prepare() treats them as missing. |

**Decisions recorded:**

- Timestamps carry +08:00; converted to Asia/Singapore local time (no daylight saving).
- indoor_co2 never reads below exactly 400 ppm: a sensor floor, so long flat stretches at 400 in an empty room are real. Declared flat_ok so they are not masked as a stuck sensor.
- wifi_connected_devices declared 'other': a proxy for occupancy, not a count of people.
- Energy columns are kWh per 5-minute interval (not cumulative), so declared as interval energy.
- ahu_fan_energy not used: identical statistics in Rooms 4 and 5 suggest a shared AHU, not room-level data.
- Data cover weekdays in separate blocks between September and December 2021; gaps between blocks stay missing.
- outdoor_relative_humidity sits at 99.9-100% for many hours on tropical nights: saturation, not a stuck sensor. Declared flat_ok.

## Preparation

- mask_spikes `air_temperature`: Single-sample spikes set to missing. (1)
- mask_spikes `indoor_relative_humidity`: Single-sample spikes set to missing. (53)
- mask_stuck `occupant_count`: 1 stuck stretch(es) set to missing. (2)
- convert_units `supply_air_flow`: Converted m3/h to m3/s.
- mask_spikes `dry_bulb_temp`: Single-sample spikes set to missing. (11)
- mask_spikes `outdoor_relative_humidity`: Single-sample spikes set to missing. (32)
- resample: Resampled to a regular 15 min grid (10368 rows). (10368)
- forward_fill `indoor_co2`: Filled input gaps up to 1h with the last known value. (31)
- forward_fill `air_temperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `indoor_relative_humidity`: Filled input gaps up to 1h with the last known value. (33)
- forward_fill `pm2.5`: Filled input gaps up to 1h with the last known value. (31)
- forward_fill `illuminance`: Filled input gaps up to 1h with the last known value. (31)
- forward_fill `voc`: Filled input gaps up to 1h with the last known value. (31)
- forward_fill `sound_pressure_level`: Filled input gaps up to 1h with the last known value. (31)
- forward_fill `wifi_connected_devices`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `occupant_count`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `occupant_presence`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `lighting_energy`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `chilled_water_energy`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `temp_setpoint`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `supply_air_temperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `damper_position`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `supply_air_flow`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `dry_bulb_temp`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `global_horizontal_solar_radiation`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `outdoor_relative_humidity`: Filled input gaps up to 1h with the last known value. (29)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2021-09-07 00:00:00+08:00 | 2021-12-13 06:45:00+08:00 | 1948 |
| val | 2021-12-13 08:00:00+08:00 | 2021-12-17 15:00:00+08:00 | 413 |
| test | 2021-12-17 16:15:00+08:00 | 2021-12-23 23:45:00+08:00 | 415 |

Time-ordered, with a 1 h gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 0.005 | 0.003 | 3.423 | 0.006 | -0.617 |
| random_forest | ml | 0.005 | 0.004 | 3.571 | -1.260 | -0.761 |
| same_time_yesterday | baseline | 0.006 | 0.004 | 3.793 | 0.005 | -0.986 |
| gbm_change | ml | 0.006 | 0.004 | 4.072 | 0.298 | -1.289 |
| gbm | ml | 0.010 | 0.007 | 6.729 | -2.351 | -5.251 |
| time_of_day_profile | baseline | 0.012 | 0.010 | 8.348 | -0.991 | -8.620 |
| ridge | ml | 0.013 | 0.009 | 8.398 | -3.738 | -8.738 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.006 | 0.006 |
| MAE (kWh) | 0.004 | 0.004 |
| CV(RMSE) % | 3.855 | 3.855 |
| NMBE % | 0.003 | 0.003 |
| R² | -0.056 | -0.056 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 3.7% (limit 30%), NMBE 0.0% (limit ±10%): **passes**.

90% prediction interval: ±0.00879 kWh (width from validation errors); it contained 88% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2021-12-13 to 2021-12-16 | 279 | 0.00 |
| 2021-12-16 to 2021-12-21 | 279 | 0.00 |
| 2021-12-21 to 2021-12-23 | 278 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| plug_load_energy (recent history) | 100% |

> Warning: No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
