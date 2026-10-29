# Run report: robod-room3-chilled_water_energy-1h

**Task:** forecast chilled_water_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)

## Data check

8352 raw rows from 2021-09-07 00:00:00+08:00 to 2021-12-23 23:55:00+08:00, typical step 5 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| warning | `index:gaps` | 7 gap(s) longer than 3 time steps, 79 d 35 min in total; longest 68 d 5 min from 2021-10-01 23:55:00+08:00 to 2021-12-09 00:00:00+08:00. | Gaps stay missing. Short gaps in inputs are forward-filled; the target is never filled. |
| info | `columns:undeclared` | 14 column(s) are not declared and will be ignored: ceiling_fan_energy, ahu_fan_energy, cooling_coil_valve_position, cooling_coil_valve_command, ahu_fan_speed, offcoil_air_temp, offcoil_temp_setpoint, pressure_across_filter .... | Declare any you want the model to use. |
| warning | `spikes:air_temperature` | 1 single-sample spike(s), e.g. 26.852 at 2021-09-10 02:15:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:indoor_relative_humidity` | 53 single-sample spike(s), e.g. 69.088, 67.0573, 65.3896 at 2021-09-07 00:15:00+08:00. | prepare() treats them as missing. |
| warning | `stuck:occupant_count` | Sensor repeats exactly 3 for 6 h 5 min (2021-12-16 12:00:00+08:00 to 2021-12-16 18:05:00+08:00); 1 such stretch(es), 6 h 5 min in total. The value is unchanged in 89% of steps and changes by at least ~1 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `missing:chilled_water_energy` | 31% of entries are missing. | Missing target values are skipped, never invented. |
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
- chilled_water_energy: whole days on which the meter read zero while the AHU fan ran with the cooling-coil valve open are set to missing (dead meter; see mask_dead_chilled_water_meter).
- Dead chilled-water meter: 9 day(s) set to missing (2021-09-24, 2021-09-27, 2021-09-28, 2021-12-09, 2021-12-10, 2021-12-13, 2021-12-14, 2021-12-15, 2021-12-16).

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
- forward_fill `plug_load_energy`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `lighting_energy`: Filled input gaps up to 1h with the last known value. (28)
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
| train | 2021-09-07 00:00:00+08:00 | 2021-09-30 23:45:00+08:00 | 1344 |
| val | 2021-10-01 01:00:00+08:00 | 2021-12-20 23:45:00+08:00 | 284 |
| test | 2021-12-21 01:00:00+08:00 | 2021-12-23 23:45:00+08:00 | 284 |

Time-ordered, with a 1 h gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 0.115 | 0.067 | 56.051 | -3.479 | 0.778 |
| gbm | ml | 0.116 | 0.063 | 56.573 | 3.744 | 0.774 |
| random_forest | ml | 0.120 | 0.066 | 58.597 | -0.188 | 0.758 |
| persistence | baseline | 0.146 | 0.071 | 71.246 | -2.998 | 0.642 |
| time_of_day_profile | baseline | 0.152 | 0.072 | 73.973 | -7.572 | 0.614 |
| same_time_yesterday | baseline | 0.202 | 0.168 | 98.285 | -8.723 | 0.319 |
| ridge | ml | 0.246 | 0.167 | 119.851 | -46.302 | -0.013 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.077 | 0.150 |
| MAE (kWh) | 0.047 | 0.064 |
| CV(RMSE) % | 36.026 | 70.479 |
| NMBE % | -6.958 | 0.000 |
| R² | 0.903 | 0.631 |

Skill vs persistence: **0.49** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 25.5% (limit 30%), NMBE -7.0% (limit ±10%): **passes**.

90% prediction interval: ±0.194 kWh (width from validation errors); it contained 96% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2021-10-01 to 2021-12-17 | 192 | 0.12 |
| 2021-12-20 to 2021-12-21 | 192 | 0.26 |
| 2021-12-22 to 2021-12-23 | 192 | 0.57 |

Pooled skill: **0.30**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| chilled_water_energy (recent history) | 55% |
| calendar (time of day, weekday) | 28% |
| supply_air_temperature | 9% |
| global_horizontal_solar_radiation | 2% |
| outdoor_relative_humidity | 2% |
| supply_air_flow | 1% |
| indoor_relative_humidity | 1% |
| damper_position | 1% |
| air_temperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
