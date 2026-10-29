# Run report: robod-room5-occupant_count-30min

**Task:** forecast occupant_count (occupancy_count, count) 30 min ahead (2 step(s) of 15 min)

## Data check

13536 raw rows from 2021-09-07 00:00:00+08:00 to 2021-12-23 23:55:00+08:00, typical step 5 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| warning | `index:gaps` | 11 gap(s) longer than 3 time steps, 61 d 55 min in total; longest 23 d 5 min from 2021-10-01 23:55:00+08:00 to 2021-10-25 00:00:00+08:00. | Gaps stay missing. Short gaps in inputs are forward-filled; the target is never filled. |
| info | `columns:undeclared` | 14 column(s) are not declared and will be ignored: ceiling_fan_energy, ahu_fan_energy, cooling_coil_valve_position, cooling_coil_valve_command, ahu_fan_speed, offcoil_air_temp, offcoil_temp_setpoint, pressure_across_filter .... | Declare any you want the model to use. |
| warning | `spikes:indoor_co2` | 4 single-sample spike(s), e.g. 559.586, 614.1, 613.25 at 2021-09-21 01:55:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:air_temperature` | 2 single-sample spike(s), e.g. 29.1868, 29.3083 at 2021-12-21 10:45:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:indoor_relative_humidity` | 18 single-sample spike(s), e.g. 67.466, 66.781, 63.5171 at 2021-09-20 00:15:00+08:00. | prepare() treats them as missing. |
| warning | `stuck:chilled_water_energy` | Sensor repeats exactly 0.484552 for 15 h 20 min (2021-11-03 18:40:00+08:00 to 2021-11-04 10:00:00+08:00); 1 such stretch(es), 15 h 20 min in total. | prepare() treats these stretches as missing. |
| warning | `stuck:supply_air_temperature` | Sensor repeats exactly 27.4455 for 6 h 20 min (2021-11-01 00:00:00+08:00 to 2021-11-01 06:20:00+08:00); 1 such stretch(es), 6 h 20 min in total. | prepare() treats these stretches as missing. |
| warning | `stuck:supply_air_flow` | Sensor repeats exactly 1942.83 for 1 d 23 h 55 min (2021-09-07 00:00:00+08:00 to 2021-09-08 23:55:00+08:00); 3 such stretch(es), 3 d 16 h 10 min in total. | prepare() treats these stretches as missing. |
| warning | `spikes:dry_bulb_temp` | 21 single-sample spike(s), e.g. 24.6033, 26.9033, 26.0046 at 2021-09-10 05:00:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:outdoor_relative_humidity` | 55 single-sample spike(s), e.g. 83.6001, 84.2, 78.985 at 2021-09-07 07:15:00+08:00. | prepare() treats them as missing. |

**Decisions recorded:**

- Timestamps carry +08:00; converted to Asia/Singapore local time (no daylight saving).
- indoor_co2 never reads below exactly 400 ppm: a sensor floor, so long flat stretches at 400 in an empty room are real. Declared flat_ok so they are not masked as a stuck sensor.
- wifi_connected_devices declared 'other': a proxy for occupancy, not a count of people.
- Energy columns are kWh per 5-minute interval (not cumulative), so declared as interval energy.
- ahu_fan_energy not used: identical statistics in Rooms 4 and 5 suggest a shared AHU, not room-level data.
- Data cover weekdays in separate blocks between September and December 2021; gaps between blocks stay missing.
- outdoor_relative_humidity sits at 99.9-100% for many hours on tropical nights: saturation, not a stuck sensor. Declared flat_ok.

## Preparation

- mask_spikes `indoor_co2`: Single-sample spikes set to missing. (4)
- mask_spikes `air_temperature`: Single-sample spikes set to missing. (2)
- mask_spikes `indoor_relative_humidity`: Single-sample spikes set to missing. (18)
- mask_stuck `chilled_water_energy`: 1 stuck stretch(es) set to missing. (113)
- mask_stuck `supply_air_temperature`: 1 stuck stretch(es) set to missing. (5)
- convert_units `supply_air_flow`: Converted m3/h to m3/s.
- mask_stuck `supply_air_flow`: 3 stuck stretch(es) set to missing. (845)
- mask_spikes `dry_bulb_temp`: Single-sample spikes set to missing. (21)
- mask_spikes `outdoor_relative_humidity`: Single-sample spikes set to missing. (55)
- incomplete_totals `chilled_water_energy`: Interval totals with missing readings set to missing (each needs 3 readings). (2)
- resample: Resampled to a regular 15 min grid (10368 rows). (10368)
- forward_fill `indoor_co2`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `air_temperature`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `indoor_relative_humidity`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `pm2.5`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `illuminance`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `voc`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `sound_pressure_level`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `wifi_connected_devices`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `occupant_presence`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `plug_load_energy`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `lighting_energy`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `chilled_water_energy`: Filled input gaps up to 1h with the last known value. (48)
- forward_fill `temp_setpoint`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `supply_air_temperature`: Filled input gaps up to 1h with the last known value. (45)
- forward_fill `damper_position`: Filled input gaps up to 1h with the last known value. (40)
- forward_fill `supply_air_flow`: Filled input gaps up to 1h with the last known value. (48)
- forward_fill `dry_bulb_temp`: Filled input gaps up to 1h with the last known value. (46)
- forward_fill `global_horizontal_solar_radiation`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `outdoor_relative_humidity`: Filled input gaps up to 1h with the last known value. (46)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2021-09-07 00:00:00+08:00 | 2021-11-12 21:15:00+08:00 | 3158 |
| val | 2021-11-12 22:00:00+08:00 | 2021-12-14 22:15:00+08:00 | 674 |
| test | 2021-12-14 23:00:00+08:00 | 2021-12-23 23:45:00+08:00 | 676 |

Time-ordered, with a 30 min gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 0.930 | 0.529 | 62.447 | -10.495 | 0.899 |
| persistence | baseline | 0.933 | 0.397 | 62.679 | -1.312 | 0.898 |
| gbm | ml | 0.957 | 0.538 | 64.277 | -15.269 | 0.893 |
| random_forest | ml | 0.982 | 0.512 | 65.962 | -11.014 | 0.887 |
| ridge | ml | 1.172 | 0.920 | 78.692 | -46.467 | 0.840 |
| time_of_day_profile | baseline | 2.709 | 1.702 | 181.938 | -46.336 | 0.142 |
| same_time_yesterday | baseline | 3.241 | 1.836 | 217.683 | -48.552 | -0.228 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 31, 'base__max_iter': 100, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (count) | 0.486 | 0.535 |
| MAE (count) | 0.249 | 0.191 |
| CV(RMSE) % | 67.084 | 73.814 |
| NMBE % | -21.525 | -0.846 |
| R² | 0.779 | 0.732 |

Skill vs persistence: **0.09** (1 = perfect, 0 = no better than the baseline).

90% prediction interval: ±1.57 count (width from validation errors); it contained 98% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2021-11-12 to 2021-12-10 | 452 | -0.01 |
| 2021-12-10 to 2021-12-17 | 451 | 0.10 |
| 2021-12-17 to 2021-12-23 | 451 | 0.22 |

Pooled skill: **0.05**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| occupant_count (recent history) | 57% |
| calendar (time of day, weekday) | 29% |
| occupant_presence | 4% |
| lighting_energy | 4% |
| sound_pressure_level | 2% |
| chilled_water_energy | 1% |
| pm2.5 | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
