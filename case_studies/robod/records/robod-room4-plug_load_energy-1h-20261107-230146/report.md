# Run report: robod-room4-plug_load_energy-1h

**Task:** forecast plug_load_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)

## Data check

13536 raw rows from 2021-09-07 00:00:00+08:00 to 2021-12-23 23:55:00+08:00, typical step 5 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| warning | `index:gaps` | 11 gap(s) longer than 3 time steps, 61 d 55 min in total; longest 23 d 5 min from 2021-10-01 23:55:00+08:00 to 2021-10-25 00:00:00+08:00. | Gaps stay missing. Short gaps in inputs are forward-filled; the target is never filled. |
| info | `columns:undeclared` | 14 column(s) are not declared and will be ignored: ceiling_fan_energy, ahu_fan_energy, cooling_coil_valve_position, cooling_coil_valve_command, ahu_fan_speed, offcoil_air_temp, offcoil_temp_setpoint, pressure_across_filter .... | Declare any you want the model to use. |
| warning | `spikes:indoor_co2` | 6 single-sample spike(s), e.g. 633.433, 580.433, 543.867 at 2021-09-07 06:55:00+08:00. | prepare() treats them as missing (by default). |
| warning | `spikes:air_temperature` | 169 single-sample spike(s), e.g. 25.9052, 25.7607, 25.876 at 2021-09-07 00:15:00+08:00. | prepare() treats them as missing (by default). |
| warning | `spikes:indoor_relative_humidity` | 52 single-sample spike(s), e.g. 76.6427, 74.8973, 79.3857 at 2021-09-14 00:10:00+08:00. | prepare() treats them as missing (by default). |
| warning | `stuck:occupant_count` | Sensor repeats exactly 1 for 7 h 5 min (2021-09-29 01:25:00+08:00 to 2021-09-29 08:30:00+08:00); 1 such stretch(es), 7 h 5 min in total. The value is unchanged in 78% of steps and changes by at least ~1 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:chilled_water_energy` | Sensor repeats exactly 0.0440593 for 11 h 45 min (2021-11-03 18:40:00+08:00 to 2021-11-04 06:25:00+08:00); 1 such stretch(es), 11 h 45 min in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:supply_air_temperature` | Sensor repeats exactly 27.4455 for 6 h 20 min (2021-11-01 00:00:00+08:00 to 2021-11-01 06:20:00+08:00); 1 such stretch(es), 6 h 20 min in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:supply_air_flow` | Sensor repeats exactly 739.639 for 1 d 3 h 15 min (2021-11-16 15:25:00+08:00 to 2021-11-17 18:40:00+08:00); 2 such stretch(es), 2 d 3 h 40 min in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:dry_bulb_temp` | 21 single-sample spike(s), e.g. 24.6033, 26.9033, 26.0046 at 2021-09-10 05:00:00+08:00. | prepare() treats them as missing (by default). |
| warning | `spikes:outdoor_relative_humidity` | 55 single-sample spike(s), e.g. 83.6001, 84.2, 78.985 at 2021-09-07 07:15:00+08:00. | prepare() treats them as missing (by default). |

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

- mask_spikes `indoor_co2`: Single-sample spikes set to missing. (6)
- mask_spikes `air_temperature`: Single-sample spikes set to missing. (169)
- mask_spikes `indoor_relative_humidity`: Single-sample spikes set to missing. (52)
- mask_stuck `occupant_count`: 1 stuck stretch(es) set to missing. (14)
- mask_stuck `chilled_water_energy`: 1 stuck stretch(es) set to missing. (70)
- mask_stuck `supply_air_temperature`: 1 stuck stretch(es) set to missing. (5)
- convert_units `supply_air_flow`: Converted m3/h to m3/s.
- mask_stuck `supply_air_flow`: 2 stuck stretch(es) set to missing. (478)
- mask_spikes `dry_bulb_temp`: Single-sample spikes set to missing. (21)
- mask_spikes `outdoor_relative_humidity`: Single-sample spikes set to missing. (55)
- incomplete_totals `chilled_water_energy`: Interval totals with missing readings set to missing (each needs 3 readings). (1)
- resample: Resampled to a regular 15 min grid (10368 rows). (10368)
- forward_fill `indoor_co2`: Filled input gaps up to 1h with the last known value. (48)
- forward_fill `air_temperature`: Filled input gaps up to 1h with the last known value. (50)
- forward_fill `indoor_relative_humidity`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `pm2.5`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `illuminance`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `voc`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `sound_pressure_level`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `wifi_connected_devices`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `occupant_count`: Filled input gaps up to 1h with the last known value. (48)
- forward_fill `occupant_presence`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `lighting_energy`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `chilled_water_energy`: Filled input gaps up to 1h with the last known value. (48)
- forward_fill `temp_setpoint`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `supply_air_temperature`: Filled input gaps up to 1h with the last known value. (45)
- forward_fill `damper_position`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `supply_air_flow`: Filled input gaps up to 1h with the last known value. (48)
- forward_fill `dry_bulb_temp`: Filled input gaps up to 1h with the last known value. (46)
- forward_fill `global_horizontal_solar_radiation`: Filled input gaps up to 1h with the last known value. (44)
- forward_fill `outdoor_relative_humidity`: Filled input gaps up to 1h with the last known value. (46)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2021-09-07 00:00:00+08:00 | 2021-11-12 21:15:00+08:00 | 3158 |
| val | 2021-11-12 22:30:00+08:00 | 2021-12-14 22:15:00+08:00 | 672 |
| test | 2021-12-14 23:30:00+08:00 | 2021-12-23 23:45:00+08:00 | 674 |

Time-ordered, with a 1 h gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 0.067 | 0.038 | 26.755 | 3.865 | 0.024 |
| gbm | ml | 0.067 | 0.041 | 26.834 | 4.100 | 0.018 |
| ridge | ml | 0.067 | 0.046 | 26.929 | 5.297 | 0.011 |
| random_forest | ml | 0.067 | 0.040 | 27.063 | 3.695 | 0.001 |
| same_time_last_week | baseline | 0.069 | 0.038 | 27.669 | 4.640 | -0.044 |
| time_of_day_profile | baseline | 0.072 | 0.051 | 29.107 | 6.105 | -0.155 |
| time_of_week_profile | baseline | 0.080 | 0.058 | 32.150 | 5.609 | -0.410 |
| towt | baseline | 0.080 | 0.058 | 32.162 | 5.991 | -0.411 |
| persistence | baseline | 0.083 | 0.037 | 33.370 | 0.118 | -0.519 |
| same_time_yesterday | baseline | 0.085 | 0.045 | 34.020 | 2.547 | -0.578 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 31, 'base__max_iter': 100, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 0.086 | 0.117 |
| MAE (kWh) | 0.066 | 0.076 |
| CV(RMSE) % | 33.773 | 46.174 |
| NMBE % | 1.949 | -0.254 |
| R² | 0.031 | -0.811 |

Skill vs same_time_last_week: **0.27** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 13.4% (limit 30%), NMBE 2.0% (limit ±10%): **passes**.

90% prediction interval: ±0.129 kWh (width from validation errors); it contained 84% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2021-11-12 to 2021-12-10 | 452 | 0.04 |
| 2021-12-10 to 2021-12-17 | 451 | 0.09 |
| 2021-12-17 to 2021-12-23 | 451 | 0.31 |

Pooled skill: **0.20**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| plug_load_energy (recent history) | 50% |
| lighting_energy | 24% |
| calendar (time of day, weekday) | 7% |
| supply_air_flow | 6% |
| indoor_relative_humidity | 5% |
| supply_air_temperature | 3% |
| pm2.5 | 2% |
| wifi_connected_devices | 1% |
| illuminance | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
