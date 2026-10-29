# Run report: t2_cw_B

**Task:** forecast chilled_water_energy (energy, kWh) 1 h ahead (4 step(s) of 15 min)

## Data check

3504 raw rows from 2021-09-07 00:00:00 to 2021-12-09 23:45:00, typical step 15 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| warning | `index:gaps` | 10 gap(s) longer than 3 time steps, 57 d 14 h 30 min in total; longest 23 d 15 min from 2021-10-01 23:45:00 to 2021-10-25 00:00:00. | Gaps stay missing. Short gaps in inputs are forward-filled; the target is never filled. |
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| info | `columns:undeclared` | 4 column(s) are not declared and will be ignored: wind_speed, indoor_co2, y, y_complete. | Declare any you want the model to use. |
| warning | `stuck:offcoil_air_temp` | Sensor repeats exactly 26.1402 for 6 h 30 min (2021-11-01 00:00:00 to 2021-11-01 06:30:00); 2 such stretch(es), 12 h 30 min in total. | prepare() treats these stretches as missing. |
| warning | `spikes:dry_bulb_temp` | 8 single-sample spike(s), e.g. 38.6328, 29.9333, 31.6333 at 2021-09-15 15:00:00. | prepare() treats them as missing. |
| warning | `stuck:outdoor_relative_humidity` | Sensor repeats exactly 99.9 for 16 h 45 min (2021-11-02 15:15:00 to 2021-11-03 08:00:00); 9 such stretch(es), 3 d 10 h 45 min in total. | prepare() treats these stretches as missing. |
| warning | `spikes:outdoor_relative_humidity` | 1 single-sample spike(s), e.g. 89.9908 at 2021-12-09 14:30:00. | prepare() treats them as missing. |

**Decisions recorded:**

- chilled_water_energy: -999 placeholders and negative values set missing; zeros while cooling-coil valve command >15% (meter outage 2021-09-21..2021-10-26, 2021-11-17 15:15..18:35) and repeated identical non-zero readings (stuck, 2021-11-03/04) set missing in own code.
- air_temperature: values >45 are degF (from 2021-11-08), converted to degC.
- wifi/occupancy columns not used: stuck for hours and unreliable; supply_air_flow/damper_position mostly missing.

## Preparation

- resample: Resampled to a regular 15 min grid (9024 rows). (9024)
- forward_fill `ahu_fan_energy`: Filled input gaps up to 1h with the last known value. (40)
- forward_fill `cooling_coil_valve_command`: Filled input gaps up to 1h with the last known value. (40)
- forward_fill `ahu_fan_speed`: Filled input gaps up to 1h with the last known value. (40)
- forward_fill `offcoil_air_temp`: Filled input gaps up to 1h with the last known value. (40)
- forward_fill `dry_bulb_temp`: Filled input gaps up to 1h with the last known value. (40)
- forward_fill `global_horizontal_solar_radiation`: Filled input gaps up to 1h with the last known value. (40)
- forward_fill `outdoor_relative_humidity`: Filled input gaps up to 1h with the last known value. (40)
- forward_fill `air_temperature`: Filled input gaps up to 1h with the last known value. (40)
- forward_fill `minute_of_day`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2021-09-07 00:00:00 | 2021-11-05 10:15:00 | 2086 |
| val | 2021-11-05 11:30:00 | 2021-11-12 03:00:00 | 443 |
| test | 2021-11-12 04:15:00 | 2021-12-09 23:45:00 | 444 |

Time-ordered, with a 1 h gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 0.675 | 0.364 | 21.972 | 0.188 | 0.963 |
| ridge | ml | 1.255 | 0.866 | 40.834 | -4.944 | 0.872 |
| same_time_yesterday | baseline | 1.960 | 1.162 | 63.747 | 5.039 | 0.687 |
| persistence | baseline | 2.133 | 0.878 | 69.392 | -2.055 | 0.630 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 31, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 0.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.798 | 2.552 |
| MAE (kWh) | 0.420 | 1.122 |
| CV(RMSE) % | 24.306 | 77.691 |
| NMBE % | 5.065 | 0.427 |
| R² | 0.956 | 0.551 |

Skill vs persistence: **0.69** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 17.6% (limit 30%), NMBE 5.1% (limit ±10%): **passes**.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
