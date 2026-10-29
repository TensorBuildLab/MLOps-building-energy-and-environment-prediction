# Run report: robod-room1-chilled_water_energy-1h

**Task:** forecast chilled_water_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)

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
- forward_fill `indoor_relative_humidity`: Filled input gaps up to 1h with the last known value. (31)
- forward_fill `pm2.5`: Filled input gaps up to 1h with the last known value. (30)
- forward_fill `illuminance`: Filled input gaps up to 1h with the last known value. (30)
- forward_fill `voc`: Filled input gaps up to 1h with the last known value. (30)
- forward_fill `sound_pressure_level`: Filled input gaps up to 1h with the last known value. (30)
- forward_fill `wifi_connected_devices`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `occupant_count`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `occupant_presence`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `plug_load_energy`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `lighting_energy`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `temp_setpoint`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `supply_air_temperature`: Filled input gaps up to 1h with the last known value. (32)
- forward_fill `dry_bulb_temp`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `global_horizontal_solar_radiation`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `outdoor_relative_humidity`: Filled input gaps up to 1h with the last known value. (29)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2021-09-07 00:00:00+08:00 | 2021-12-13 07:00:00+08:00 | 1945 |
| val | 2021-12-13 08:15:00+08:00 | 2021-12-17 15:15:00+08:00 | 413 |
| test | 2021-12-17 16:30:00+08:00 | 2021-12-23 23:45:00+08:00 | 414 |

Time-ordered, with a 1 h gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 1.481 | 0.998 | 269.794 | -107.318 | -0.032 |
| ridge | ml | 1.490 | 1.083 | 271.444 | -50.155 | -0.045 |
| persistence | baseline | 1.491 | 0.480 | 271.684 | -4.858 | -0.046 |
| random_forest | ml | 1.497 | 1.043 | 272.745 | -117.173 | -0.055 |
| gbm | ml | 1.646 | 1.190 | 299.825 | -149.600 | -0.274 |
| same_time_yesterday | baseline | 2.038 | 1.050 | 371.231 | -37.421 | -0.954 |
| time_of_day_profile | baseline | 2.153 | 1.571 | 392.139 | -237.867 | -1.180 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 1.265 | 1.096 |
| MAE (kWh) | 0.703 | 0.268 |
| CV(RMSE) % | 569.808 | 493.830 |
| NMBE % | -110.538 | -6.682 |
| R² | -0.603 | -0.204 |

Skill vs persistence: **-0.15** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 510.9% (limit 30%), NMBE -111.3% (limit ±10%): **does not pass**.

90% prediction interval: ±2.29 kWh (width from validation errors); it contained 93% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2021-12-13 to 2021-12-16 | 279 | 0.03 |
| 2021-12-16 to 2021-12-21 | 278 | -0.10 |
| 2021-12-21 to 2021-12-23 | 278 | 0.01 |

Pooled skill: **-0.02**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| chilled_water_energy (recent history) | 65% |
| global_horizontal_solar_radiation | 9% |
| plug_load_energy | 8% |
| supply_air_temperature | 6% |
| lighting_energy | 6% |
| outdoor_relative_humidity | 3% |
| pm2.5 | 3% |
| temp_setpoint | 2% |

> Warning: The model is barely better than persistence on test data (skill -0.15).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
