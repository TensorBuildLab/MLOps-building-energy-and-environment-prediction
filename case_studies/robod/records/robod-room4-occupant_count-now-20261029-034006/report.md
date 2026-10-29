# Run report: robod-room4-occupant_count-now

**Task:** estimate occupant_count (occupancy_count, count) at the same moment as its inputs (estimation / virtual sensor)

## Data check

13536 raw rows from 2021-09-07 00:00:00+08:00 to 2021-12-23 23:55:00+08:00, typical step 5 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| warning | `index:gaps` | 11 gap(s) longer than 3 time steps, 61 d 55 min in total; longest 23 d 5 min from 2021-10-01 23:55:00+08:00 to 2021-10-25 00:00:00+08:00. | Gaps stay missing. Short gaps in inputs are forward-filled; the target is never filled. |
| info | `columns:undeclared` | 15 column(s) are not declared and will be ignored: ceiling_fan_energy, ahu_fan_energy, cooling_coil_valve_position, cooling_coil_valve_command, ahu_fan_speed, offcoil_air_temp, offcoil_temp_setpoint, pressure_across_filter .... | Declare any you want the model to use. |
| warning | `spikes:indoor_co2` | 6 single-sample spike(s), e.g. 633.433, 580.433, 543.867 at 2021-09-07 06:55:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:air_temperature` | 169 single-sample spike(s), e.g. 25.9052, 25.7607, 25.876 at 2021-09-07 00:15:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:indoor_relative_humidity` | 52 single-sample spike(s), e.g. 76.6427, 74.8973, 79.3857 at 2021-09-14 00:10:00+08:00. | prepare() treats them as missing. |
| warning | `stuck:occupant_count` | Sensor repeats exactly 1 for 7 h 5 min (2021-09-29 01:25:00+08:00 to 2021-09-29 08:30:00+08:00); 1 such stretch(es), 7 h 5 min in total. The value is unchanged in 78% of steps and changes by at least ~1 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:chilled_water_energy` | Sensor repeats exactly 0.0440593 for 11 h 45 min (2021-11-03 18:40:00+08:00 to 2021-11-04 06:25:00+08:00); 1 such stretch(es), 11 h 45 min in total. | prepare() treats these stretches as missing. |
| warning | `stuck:supply_air_temperature` | Sensor repeats exactly 27.4455 for 6 h 20 min (2021-11-01 00:00:00+08:00 to 2021-11-01 06:20:00+08:00); 1 such stretch(es), 6 h 20 min in total. | prepare() treats these stretches as missing. |
| warning | `stuck:supply_air_flow` | Sensor repeats exactly 739.639 for 1 d 3 h 15 min (2021-11-16 15:25:00+08:00 to 2021-11-17 18:40:00+08:00); 2 such stretch(es), 2 d 3 h 40 min in total. | prepare() treats these stretches as missing. |
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
- occupant_presence excluded: it comes from the same camera ground truth as the target, so it would leak the answer.

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
- forward_fill `plug_load_energy`: Filled input gaps up to 1h with the last known value. (44)
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
| train | 2021-09-07 00:00:00+08:00 | 2021-11-12 21:30:00+08:00 | 3155 |
| val | 2021-11-12 21:45:00+08:00 | 2021-12-14 22:30:00+08:00 | 676 |
| test | 2021-12-14 22:45:00+08:00 | 2021-12-23 23:45:00+08:00 | 677 |

Time-ordered, with a 0 s gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 2.222 | 1.461 | 88.836 | -41.671 | 0.384 |
| time_of_day_profile | baseline | 2.252 | 1.408 | 90.031 | -44.950 | 0.368 |
| random_forest | ml | 2.371 | 1.466 | 94.775 | -46.508 | 0.299 |
| gbm | ml | 2.640 | 1.541 | 105.551 | -48.304 | 0.131 |
| training_mean | baseline | 3.051 | 2.778 | 121.944 | -45.324 | -0.160 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (count) | 1.359 | 1.360 |
| MAE (count) | 1.009 | 0.928 |
| CV(RMSE) % | 49.189 | 49.210 |
| NMBE % | -11.076 | -23.829 |
| R² | 0.783 | 0.783 |

Skill vs time_of_day_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

90% prediction interval: ±3.29 count (width from validation errors); it contained 96% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2021-11-12 to 2021-12-10 | 451 | 0.03 |
| 2021-12-10 to 2021-12-17 | 451 | -0.05 |
| 2021-12-17 to 2021-12-23 | 451 | 0.06 |

Pooled skill: **0.02**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 41% |
| chilled_water_energy | 24% |
| supply_air_flow | 18% |
| supply_air_temperature | 7% |
| illuminance | 2% |
| damper_position | 2% |
| wifi_connected_devices | 2% |
| lighting_energy | 2% |
| pm2.5 | 1% |
| outdoor_relative_humidity | 1% |

> Warning: The model is barely better than time_of_day_profile on test data (skill 0.00).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
