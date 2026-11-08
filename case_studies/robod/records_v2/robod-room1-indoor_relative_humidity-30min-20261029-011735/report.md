# Run report: robod-room1-indoor_relative_humidity-30min

**Task:** forecast indoor_relative_humidity (relative_humidity, %) 30 min ahead (2 step(s) of 15 min)

## Data check

8352 raw rows from 2021-09-07 00:00:00+08:00 to 2021-12-23 23:55:00+08:00, typical step 5 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| warning | `index:gaps` | 7 gap(s) longer than 3 time steps, 79 d 35 min in total; longest 68 d 5 min from 2021-10-01 23:55:00+08:00 to 2021-12-09 00:00:00+08:00. | Gaps stay missing. Short gaps in inputs are forward-filled; the target is never filled. |
| info | `columns:undeclared` | 8 column(s) are not declared and will be ignored: ceiling_fan_energy, fcu_fan_energy, fcu_fan_speed, supply_air_pressure, baromatic_pressure, wind_direction, wind_speed, outdoor_co2. | Declare any you want the model to use. |
| warning | `spikes:indoor_co2` | 57 single-sample spike(s), e.g. 498.533, 551.933, 583.207 at 2021-09-07 01:00:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:air_temperature` | 44 single-sample spike(s), e.g. 26.44, 26.1561, 25.69 at 2021-09-07 23:45:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:indoor_relative_humidity` | 56 single-sample spike(s), e.g. 68.5957, 66.8783, 69.277 at 2021-09-07 23:40:00+08:00. | prepare() treats them as missing. |
| warning | `stuck:supply_air_temperature` | Sensor repeats exactly 27.3021 for 7 h 40 min (2021-12-13 00:20:00+08:00 to 2021-12-13 08:00:00+08:00); 1 such stretch(es), 7 h 40 min in total. | prepare() treats these stretches as missing. |
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

- mask_spikes `indoor_co2`: Single-sample spikes set to missing. (57)
- mask_spikes `air_temperature`: Single-sample spikes set to missing. (44)
- mask_spikes `indoor_relative_humidity`: Single-sample spikes set to missing. (56)
- mask_stuck `supply_air_temperature`: 1 stuck stretch(es) set to missing. (21)
- mask_spikes `dry_bulb_temp`: Single-sample spikes set to missing. (11)
- mask_spikes `outdoor_relative_humidity`: Single-sample spikes set to missing. (32)
- incomplete_totals `chilled_water_energy`: Interval totals with missing readings set to missing (each needs 3 readings). (2)
- resample: Resampled to a regular 15 min grid (10368 rows). (10368)
- forward_fill `indoor_co2`: Filled input gaps up to 1h with the last known value. (40)
- forward_fill `air_temperature`: Filled input gaps up to 1h with the last known value. (32)
- forward_fill `pm2.5`: Filled input gaps up to 1h with the last known value. (30)
- forward_fill `illuminance`: Filled input gaps up to 1h with the last known value. (30)
- forward_fill `voc`: Filled input gaps up to 1h with the last known value. (30)
- forward_fill `sound_pressure_level`: Filled input gaps up to 1h with the last known value. (30)
- forward_fill `wifi_connected_devices`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `occupant_count`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `occupant_presence`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `plug_load_energy`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `lighting_energy`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `chilled_water_energy`: Filled input gaps up to 1h with the last known value. (32)
- forward_fill `temp_setpoint`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `supply_air_temperature`: Filled input gaps up to 1h with the last known value. (32)
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
| persistence | baseline | 2.457 | 1.036 | 3.265 | 0.005 | 0.867 |
| gbm_change | ml | 2.495 | 1.574 | 3.315 | 0.490 | 0.863 |
| ridge | ml | 3.033 | 2.077 | 4.030 | -0.389 | 0.797 |
| random_forest | ml | 3.343 | 1.882 | 4.442 | -0.897 | 0.754 |
| gbm | ml | 3.679 | 2.223 | 4.888 | -0.694 | 0.702 |
| time_of_day_profile | baseline | 5.920 | 4.160 | 7.866 | -1.618 | 0.227 |
| same_time_yesterday | baseline | 8.251 | 5.610 | 10.963 | -1.213 | -0.501 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (%) | 2.271 | 2.271 |
| MAE (%) | 0.953 | 0.953 |
| CV(RMSE) % | 3.318 | 3.318 |
| NMBE % | -0.120 | -0.120 |
| R² | 0.917 | 0.917 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

90% prediction interval: ±2.33 % (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2021-12-13 to 2021-12-16 | 279 | 0.00 |
| 2021-12-16 to 2021-12-21 | 278 | 0.00 |
| 2021-12-21 to 2021-12-23 | 278 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| indoor_relative_humidity (recent history) | 100% |

> Warning: No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
