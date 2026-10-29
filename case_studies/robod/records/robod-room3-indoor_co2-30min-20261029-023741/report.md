# Run report: robod-room3-indoor_co2-30min

**Task:** forecast indoor_co2 (co2, ppm) 30 min ahead (2 step(s) of 15 min)

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
- forward_fill `air_temperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `indoor_relative_humidity`: Filled input gaps up to 1h with the last known value. (33)
- forward_fill `pm2.5`: Filled input gaps up to 1h with the last known value. (31)
- forward_fill `illuminance`: Filled input gaps up to 1h with the last known value. (31)
- forward_fill `voc`: Filled input gaps up to 1h with the last known value. (31)
- forward_fill `sound_pressure_level`: Filled input gaps up to 1h with the last known value. (31)
- forward_fill `wifi_connected_devices`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `occupant_count`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `occupant_presence`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `plug_load_energy`: Filled input gaps up to 1h with the last known value. (28)
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
| train | 2021-09-07 00:00:00+08:00 | 2021-12-13 06:15:00+08:00 | 1946 |
| val | 2021-12-13 07:00:00+08:00 | 2021-12-17 14:45:00+08:00 | 415 |
| test | 2021-12-17 15:30:00+08:00 | 2021-12-23 23:45:00+08:00 | 416 |

Time-ordered, with a 30 min gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 12.338 | 7.934 | 2.536 | 0.370 | 0.917 |
| persistence | baseline | 13.298 | 8.204 | 2.733 | -0.002 | 0.904 |
| ridge | ml | 15.460 | 8.305 | 3.177 | 0.369 | 0.870 |
| gbm | ml | 16.182 | 9.773 | 3.325 | 0.468 | 0.857 |
| random_forest | ml | 20.297 | 10.741 | 4.171 | 0.196 | 0.776 |
| time_of_day_profile | baseline | 40.353 | 34.725 | 8.293 | 0.027 | 0.113 |
| same_time_yesterday | baseline | 55.395 | 40.871 | 11.384 | -1.180 | -0.672 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 31, 'base__max_iter': 100, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (ppm) | 10.757 | 11.172 |
| MAE (ppm) | 6.266 | 5.854 |
| CV(RMSE) % | 2.336 | 2.426 |
| NMBE % | 0.076 | 0.074 |
| R² | 0.918 | 0.911 |

Skill vs persistence: **0.04** (1 = perfect, 0 = no better than the baseline).

90% prediction interval: ±17.7 ppm (width from validation errors); it contained 95% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2021-12-13 to 2021-12-16 | 279 | 0.10 |
| 2021-12-16 to 2021-12-21 | 278 | 0.03 |
| 2021-12-21 to 2021-12-23 | 278 | -0.25 |

Pooled skill: **0.03**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| indoor_co2 (recent history) | 96% |
| calendar (time of day, weekday) | 2% |
| sound_pressure_level | 1% |

> Warning: The model is barely better than persistence on test data (skill 0.04).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
