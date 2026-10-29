# Run report: robod-room2-chilled_water_energy-1h

**Task:** forecast chilled_water_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)

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
| train | 2021-09-07 00:00:00+08:00 | 2021-12-13 06:45:00+08:00 | 1948 |
| val | 2021-12-13 08:00:00+08:00 | 2021-12-17 15:00:00+08:00 | 413 |
| test | 2021-12-17 16:15:00+08:00 | 2021-12-23 23:45:00+08:00 | 415 |

Time-ordered, with a 1 h gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 0.418 | 0.114 | 134.928 | 10.193 | 0.785 |
| random_forest | ml | 0.743 | 0.522 | 239.864 | -108.629 | 0.321 |
| gbm | ml | 0.779 | 0.559 | 251.695 | -105.568 | 0.252 |
| ridge | ml | 0.852 | 0.618 | 275.110 | -67.698 | 0.106 |
| same_time_yesterday | baseline | 1.017 | 0.433 | 328.383 | 25.101 | -0.273 |
| gbm_change | ml | 1.104 | 0.837 | 356.555 | -183.662 | -0.501 |
| time_of_day_profile | baseline | 1.327 | 0.965 | 428.606 | -241.365 | -1.169 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.978 | 0.978 |
| MAE (kWh) | 0.379 | 0.379 |
| CV(RMSE) % | 126.931 | 126.931 |
| NMBE % | -5.470 | -5.470 |
| R² | 0.524 | 0.524 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 103.1% (limit 30%), NMBE -5.5% (limit ±10%): **does not pass**.

90% prediction interval: ±0.0156 kWh (width from validation errors); it contained 75% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2021-12-13 to 2021-12-16 | 279 | 0.00 |
| 2021-12-16 to 2021-12-21 | 279 | 0.00 |
| 2021-12-21 to 2021-12-23 | 278 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| chilled_water_energy (recent history) | 100% |

> Warning: No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
