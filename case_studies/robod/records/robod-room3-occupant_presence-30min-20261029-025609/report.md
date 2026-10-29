# Run report: robod-room3-occupant_presence-30min

**Task:** forecast yes/no occupant_presence (occupancy_status, binary) 30 min ahead (2 step(s) of 15 min)

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
| train | 2021-09-07 00:00:00+08:00 | 2021-12-13 06:45:00+08:00 | 1948 |
| val | 2021-12-13 07:30:00+08:00 | 2021-12-17 15:00:00+08:00 | 415 |
| test | 2021-12-17 15:45:00+08:00 | 2021-12-23 23:45:00+08:00 | 417 |

Time-ordered, with a 30 min gap between sets.

## Validation

| model | type | Brier score | Accuracy | Balanced accuracy | F1 | ROC AUC |
|---|---|---|---|---|---|---|
| random_forest | ml | 0.042 | 0.947 | 0.947 | 0.934 | 0.982 |
| gbm | ml | 0.045 | 0.928 | 0.932 | 0.912 | 0.990 |
| logistic | ml | 0.052 | 0.916 | 0.921 | 0.899 | 0.980 |
| persistence | baseline | 0.053 | 0.945 | 0.942 | 0.930 | 0.949 |
| same_time_yesterday | baseline | 0.095 | 0.846 | 0.823 | 0.785 | 0.932 |

## Test result

Chosen model: **random_forest** {'model__min_samples_leaf': 10, 'model__max_features': 0.6, 'model__max_depth': 16}

| Metric | Model | persistence |
|---|---|---|
| Brier score | 0.045 | 0.041 |
| Accuracy | 0.962 | 0.959 |
| Balanced accuracy | 0.943 | 0.945 |
| F1 | 0.918 | 0.914 |
| ROC AUC | 0.991 | 0.947 |

Skill vs persistence: **-0.09** (1 = perfect, 0 = no better than the baseline).

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2021-12-13 to 2021-12-16 | 279 | 0.32 |
| 2021-12-16 to 2021-12-21 | 279 | 0.18 |
| 2021-12-21 to 2021-12-23 | 278 | -0.46 |

Pooled skill: **0.09**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| occupant_presence (recent history) | 44% |
| calendar (time of day, weekday) | 25% |
| occupant_count | 25% |
| damper_position | 3% |
| plug_load_energy | 1% |
| illuminance | 1% |

> Warning: The model is barely better than persistence on test data (skill -0.09).

## Plots

![timeseries](test_timeseries.png)
