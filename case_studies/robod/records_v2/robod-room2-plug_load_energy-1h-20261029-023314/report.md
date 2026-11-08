# Run report: robod-room2-plug_load_energy-1h

**Task:** forecast plug_load_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)

## Data check

8352 raw rows from 2021-09-07 00:00:00+08:00 to 2021-12-23 23:55:00+08:00, typical step 5 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| warning | `index:gaps` | 7 gap(s) longer than 3 time steps, 79 d 35 min in total; longest 68 d 5 min from 2021-10-01 23:55:00+08:00 to 2021-12-09 00:00:00+08:00. | Gaps stay missing. Short gaps in inputs are forward-filled; the target is never filled. |
| info | `columns:undeclared` | 8 column(s) are not declared and will be ignored: ceiling_fan_energy, fcu_fan_energy, fcu_fan_speed, supply_air_pressure, baromatic_pressure, wind_direction, wind_speed, outdoor_co2. | Declare any you want the model to use. |
| warning | `spikes:indoor_co2` | 118 single-sample spike(s), e.g. 641.933, 679, 551.1 at 2021-09-07 06:10:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:air_temperature` | 17 single-sample spike(s), e.g. 27.6765, 25.1713, 24.885 at 2021-09-17 07:35:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:indoor_relative_humidity` | 21 single-sample spike(s), e.g. 79.2087, 80.6548, 80.1367 at 2021-09-27 09:20:00+08:00. | prepare() treats them as missing. |
| warning | `stuck:supply_air_temperature` | Sensor repeats exactly 27.3021 for 7 h 40 min (2021-12-13 00:20:00+08:00 to 2021-12-13 08:00:00+08:00); 1 such stretch(es), 7 h 40 min in total. | prepare() treats these stretches as missing. |
| warning | `spikes:dry_bulb_temp` | 15 single-sample spike(s), e.g. 24.6033, 32.1, 30.9 at 2021-09-10 05:00:00+08:00. | prepare() treats them as missing. |
| warning | `spikes:outdoor_relative_humidity` | 34 single-sample spike(s), e.g. 83.6001, 84.2, 78.985 at 2021-09-07 07:15:00+08:00. | prepare() treats them as missing. |

**Decisions recorded:**

- Timestamps carry +08:00; converted to Asia/Singapore local time (no daylight saving).
- indoor_co2 never reads below exactly 400 ppm: a sensor floor, so long flat stretches at 400 in an empty room are real. Declared flat_ok so they are not masked as a stuck sensor.
- wifi_connected_devices declared 'other': a proxy for occupancy, not a count of people.
- Energy columns are kWh per 5-minute interval (not cumulative), so declared as interval energy.
- ahu_fan_energy not used: identical statistics in Rooms 4 and 5 suggest a shared AHU, not room-level data.
- Data cover weekdays in separate blocks between September and December 2021; gaps between blocks stay missing.
- outdoor_relative_humidity sits at 99.9-100% for many hours on tropical nights: saturation, not a stuck sensor. Declared flat_ok.

## Preparation

- mask_spikes `indoor_co2`: Single-sample spikes set to missing. (118)
- mask_spikes `air_temperature`: Single-sample spikes set to missing. (17)
- mask_spikes `indoor_relative_humidity`: Single-sample spikes set to missing. (21)
- mask_stuck `supply_air_temperature`: 1 stuck stretch(es) set to missing. (21)
- mask_spikes `dry_bulb_temp`: Single-sample spikes set to missing. (15)
- mask_spikes `outdoor_relative_humidity`: Single-sample spikes set to missing. (34)
- resample: Resampled to a regular 15 min grid (10368 rows). (10368)
- forward_fill `indoor_co2`: Filled input gaps up to 1h with the last known value. (52)
- forward_fill `air_temperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `indoor_relative_humidity`: Filled input gaps up to 1h with the last known value. (33)
- forward_fill `pm2.5`: Filled input gaps up to 1h with the last known value. (32)
- forward_fill `illuminance`: Filled input gaps up to 1h with the last known value. (32)
- forward_fill `voc`: Filled input gaps up to 1h with the last known value. (32)
- forward_fill `sound_pressure_level`: Filled input gaps up to 1h with the last known value. (32)
- forward_fill `wifi_connected_devices`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `occupant_count`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `occupant_presence`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `lighting_energy`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `chilled_water_energy`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `temp_setpoint`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `supply_air_temperature`: Filled input gaps up to 1h with the last known value. (32)
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
| gbm | ml | 0.424 | 0.183 | 303.966 | -26.652 | 0.153 |
| random_forest | ml | 0.439 | 0.120 | 314.742 | 25.450 | 0.092 |
| ridge | ml | 0.462 | 0.156 | 330.782 | -19.139 | -0.003 |
| time_of_day_profile | baseline | 0.467 | 0.143 | 334.615 | 29.056 | -0.026 |
| gbm_change | ml | 0.526 | 0.156 | 377.137 | -16.779 | -0.303 |
| persistence | baseline | 0.539 | 0.127 | 385.917 | 0.475 | -0.365 |
| same_time_yesterday | baseline | 0.639 | 0.190 | 458.020 | 0.604 | -0.922 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 0.1}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 0.310 | 0.370 |
| MAE (kWh) | 0.113 | 0.128 |
| CV(RMSE) % | 232.659 | 277.757 |
| NMBE % | 3.434 | 21.947 |
| R² | 0.342 | 0.063 |

Skill vs time_of_day_profile: **0.16** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 226.9% (limit 30%), NMBE 3.5% (limit ±10%): **does not pass**.

90% prediction interval: ±0.261 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2021-12-13 to 2021-12-16 | 279 | 0.07 |
| 2021-12-16 to 2021-12-21 | 279 | 0.09 |
| 2021-12-21 to 2021-12-23 | 278 | 0.16 |

Pooled skill: **0.11**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| plug_load_energy (recent history) | 44% |
| calendar (time of day, weekday) | 21% |
| air_temperature | 13% |
| temp_setpoint | 10% |
| indoor_co2 | 7% |
| pm2.5 | 2% |
| global_horizontal_solar_radiation | 2% |
| indoor_relative_humidity | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
