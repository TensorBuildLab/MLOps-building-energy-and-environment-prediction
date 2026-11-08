# Run report: robod-room3-occupant_count-30min

**Task:** forecast occupant_count (occupancy_count, count) 30 min ahead (2 step(s) of 15 min)

## Data check

8352 raw rows from 2021-09-07 00:00:00+08:00 to 2021-12-23 23:55:00+08:00, typical step 5 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| warning | `index:gaps` | 7 gap(s) longer than 3 time steps, 79 d 35 min in total; longest 68 d 5 min from 2021-10-01 23:55:00+08:00 to 2021-12-09 00:00:00+08:00. | Gaps stay missing. Short gaps in inputs are forward-filled; the target is never filled. |
| info | `columns:undeclared` | 14 column(s) are not declared and will be ignored: ceiling_fan_energy, ahu_fan_energy, cooling_coil_valve_position, cooling_coil_valve_command, ahu_fan_speed, offcoil_air_temp, offcoil_temp_setpoint, pressure_across_filter .... | Declare any you want the model to use. |
| warning | `spikes:air_temperature` | 1 single-sample spike(s), e.g. 26.852 at 2021-09-10 02:15:00+08:00. | prepare() treats them as missing (by default). |
| warning | `spikes:indoor_relative_humidity` | 53 single-sample spike(s), e.g. 69.088, 67.0573, 65.3896 at 2021-09-07 00:15:00+08:00. | prepare() treats them as missing (by default). |
| warning | `stuck:occupant_count` | Sensor repeats exactly 3 for 6 h 5 min (2021-12-16 12:00:00+08:00 to 2021-12-16 18:05:00+08:00); 1 such stretch(es), 6 h 5 min in total. The value is unchanged in 89% of steps and changes by at least ~1 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `missing:chilled_water_energy` | 31% of entries are missing. | Models that need complete inputs fill them with the training median. |
| warning | `spikes:dry_bulb_temp` | 11 single-sample spike(s), e.g. 24.6033, 26.9033, 26.0046 at 2021-09-10 05:00:00+08:00. | prepare() treats them as missing (by default). |
| warning | `spikes:outdoor_relative_humidity` | 32 single-sample spike(s), e.g. 83.6001, 84.2, 78.985 at 2021-09-07 07:15:00+08:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Timestamps carry +08:00; converted to Asia/Singapore local time (no daylight saving).
- indoor_co2 never reads below exactly 400 ppm: a sensor floor, so long flat stretches at 400 in an empty room are real. Declared flat_ok so they are not masked as a stuck sensor.
- wifi_connected_devices declared 'other': a proxy for occupancy, not a count of people.
- Energy columns are kWh per 5-minute interval (not cumulative), so declared as interval energy.
- ahu_fan_energy not used: identical statistics in Rooms 4 and 5 suggest a shared AHU, not room-level data.
- Data cover weekdays in separate blocks between September and December 2021; gaps between blocks stay missing.
- outdoor_relative_humidity sits at 99.9-100% for many hours on tropical nights: saturation, not a stuck sensor. Declared flat_ok.
- chilled_water_energy: whole days on which the meter read zero while the AHU fan ran with the cooling-coil valve open are set to missing (dead meter; see mask_dead_chilled_water_meter).

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
- forward_fill `occupant_presence`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `plug_load_energy`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `lighting_energy`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `chilled_water_energy`: Filled input gaps up to 1h with the last known value. (24)
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
| val | 2021-12-13 07:30:00+08:00 | 2021-12-17 15:00:00+08:00 | 415 |
| test | 2021-12-17 15:45:00+08:00 | 2021-12-23 23:45:00+08:00 | 417 |

Time-ordered, with a 30 min gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 0.772 | 0.443 | 56.441 | -11.208 | 0.865 |
| gbm_change | ml | 0.789 | 0.441 | 57.671 | -7.238 | 0.859 |
| random_forest | ml | 0.801 | 0.447 | 58.553 | -12.739 | 0.854 |
| persistence | baseline | 0.878 | 0.380 | 64.187 | 0.176 | 0.825 |
| ridge | ml | 0.887 | 0.586 | 64.844 | -13.524 | 0.821 |
| towt | baseline | 1.411 | 0.847 | 103.153 | -47.684 | 0.548 |
| time_of_week_profile | baseline | 1.427 | 0.844 | 104.291 | -49.361 | 0.538 |
| time_of_day_profile | baseline | 1.494 | 0.892 | 109.224 | -46.173 | 0.494 |
| same_time_yesterday | baseline | 1.549 | 0.929 | 113.239 | -12.213 | 0.456 |
| same_time_last_week | baseline | 2.071 | 1.548 | 151.396 | -15.918 | 0.027 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 50, 'max_leaf_nodes': 31, 'max_iter': 100, 'learning_rate': 0.05, 'l2_regularization': 0.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (count) | 0.731 | 0.647 |
| MAE (count) | 0.375 | 0.172 |
| CV(RMSE) % | 182.725 | 161.681 |
| NMBE % | -68.786 | -2.512 |
| R² | 0.356 | 0.495 |

Skill vs persistence: **-0.13** (1 = perfect, 0 = no better than the baseline).

90% prediction interval: ±1.22 count (width from validation errors); it contained 93% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2021-12-13 to 2021-12-16 | 279 | 0.17 |
| 2021-12-16 to 2021-12-21 | 279 | 0.02 |
| 2021-12-21 to 2021-12-23 | 278 | -0.97 |

Pooled skill: **0.04**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| occupant_count (recent history) | 66% |
| calendar (time of day, weekday) | 13% |
| damper_position | 6% |
| global_horizontal_solar_radiation | 5% |
| occupant_presence | 4% |
| air_temperature | 2% |
| indoor_relative_humidity | 2% |
| dry_bulb_temp | 1% |
| supply_air_temperature | 1% |

> Warning: The model is barely better than persistence on test data (skill -0.13).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
