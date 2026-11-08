# Run report: aalborg-roomd-people-amount-1h

**Task:** forecast RoomD:People__amount (occupancy_count, count) 1 h ahead (4 step(s) of 15 min)

## Data check

88705 raw rows from 2023-02-27 00:00:00+01:00 to 2024-01-01 00:00:00+01:00, typical step 5 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `columns:undeclared` | 167 column(s) are not declared and will be ignored: Heating:Control__setpoint_water_temperature__supply, Heating:DH__energy_accumulated, Heating:DH__operation_hours_accumulated, Heating:DH__water_flow, Heating:DH__water_flow_accumulated, Heating:DH__water_temperature__return, Heating:DH__water_temperature__supply, Heating:Mixing_valve__control_signal .... | Declare any you want the model to use. |
| warning | `stuck:Outdoor:Temperature_air` | Sensor repeats exactly 4.99997 for 1 d 13 h 15 min (2023-11-19 06:15:00+01:00 to 2023-11-20 19:30:00+01:00); 60 such stretch(es), 26 d 10 h 30 min in total. | prepare() treats these stretches as missing. |
| warning | `stuck:Outdoor:Wind__velocity` | Sensor repeats exactly 0.64299 for 1 d 1 h 20 min (2023-02-28 11:15:00+01:00 to 2023-03-01 12:35:00+01:00); 116 such stretch(es), 46 d 3 h 20 min in total. The value is unchanged in 82% of steps and changes by at least ~0.20278 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `spikes:Outdoor:Wind__velocity` | 289 single-sample spike(s), e.g. 4.20511, 4.61631, 4.64302 at 2023-03-23 11:10:00+01:00. | prepare() treats them as missing. |
| warning | `spikes:RoomD:Sensor__CO2` | 122 single-sample spike(s), e.g. 400, 527, 772 at 2023-03-07 15:00:00+01:00. | prepare() treats them as missing. |
| warning | `spikes:RoomD:Sensor__room_temperature` | 32 single-sample spike(s), e.g. 23.16, 23.04, 25.3 at 2023-03-31 01:35:00+02:00. | prepare() treats them as missing. |
| warning | `missing:RoomD:People__amount` | 40% of entries are missing. | Missing target values are skipped, never invented. |

**Accepted as-is (with reasons):**

- `missing:RoomD:People__amount`: Camera people counts were only recorded for part of the year (documented by the dataset authors). Missing targets are skipped, never filled; results cover the recorded periods.

**Decisions recorded:**

- Timestamps carry UTC offsets that switch at daylight saving; converted to Europe/Copenhagen local time with the zone kept, so the repeated autumn hour and the missing spring hour are handled exactly.
- Units are not in the headers. Inferred from magnitudes and the dataset paper: district-heating, heating-coil and ventilation electric power in W, supply air flow in m3/h, temperatures in degC.
- Facade solar sensors never read exactly zero (night offset of 2-4 W/m2), so long flat night stretches are real: declared flat_ok.
- Heating:DH__energy_accumulated and Ventilation:EL_meter__energy_accumulated are cumulative meters; not used, since the matching power points carry the same information per interval.
- Room CO2 is logged on change of value: in Room A the reading is unchanged in 95% of 5-minute steps and moves by at least ~34 ppm when it changes (vs 9% unchanged for room temperature). Long flat stretches are therefore expected, not stuck sensors: CO2 declared flat_ok in every room.
- Outdoor temperature is NOT logged that way (34% unchanged, tiny steps), so its flat stretches (e.g. 4.99997 degC for 37 h in November) are real faults and stay masked. Wind speed looks change-of-value logged too, but 25-hour holds are implausible, so it is left to masking (it is only an input).
- Room ventilation and heating are served by building systems that also serve other spaces; system points are inputs to room tasks, not room-level loads.

## Preparation

- mask_stuck `Outdoor:Temperature_air`: 60 stuck stretch(es) set to missing. (3354)
- mask_stuck `Outdoor:Wind__velocity`: 116 stuck stretch(es) set to missing. (5052)
- mask_spikes `Outdoor:Wind__velocity`: Single-sample spikes set to missing. (286)
- convert_units `Ventilation:EL_meter__power`: Converted W to kW.
- convert_units `Ventilation:Fan__air_flow__supply`: Converted m3/h to m3/s.
- convert_units `Heating:DH__power`: Converted W to kW.
- convert_units `Ventilation:HC__power`: Converted W to kW.
- mask_spikes `RoomD:Sensor__CO2`: Single-sample spikes set to missing. (122)
- mask_spikes `RoomD:Sensor__room_temperature`: Single-sample spikes set to missing. (32)
- resample: Resampled to a regular 15 min grid (29569 rows). (29569)
- forward_fill `Outdoor:Temperature_air`: Filled input gaps up to 1h with the last known value. (279)
- forward_fill `Outdoor:Wind__velocity`: Filled input gaps up to 1h with the last known value. (379)
- forward_fill `Outdoor:Solar__direct_radiation__east_façade`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Outdoor:Solar__direct_radiation__south_façade`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Outdoor:Solar__direct_radiation__west_façade`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Ventilation:EL_meter__power`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Ventilation:Fan__air_flow__supply`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Ventilation:Sensor__air_temperature__supply`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Heating:DH__power`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Ventilation:HC__power`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `RoomD:Sensor__CO2`: Filled input gaps up to 1h with the last known value. (7)
- forward_fill `RoomD:Sensor__room_temperature`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `RoomD:Room__active`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `RoomD:Damper__position`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `RoomD:Radiator__control_signal__motor_valve`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `RoomD:Light__level__ceiling`: Filled input gaps up to 1h with the last known value. (6)
- forward_fill `RoomD:Light__on_off_signal`: Filled input gaps up to 1h with the last known value. (6)
- forward_fill `RoomD:Window__opened_closed`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `RoomD:Control__setpoint_temperature_global`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `RoomD:Control__heating_limit`: Filled input gaps up to 1h with the last known value. (6)
- forward_fill `RoomD:Control__cooling_limit`: Filled input gaps up to 1h with the last known value. (6)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2023-02-27 00:00:00+01:00 | 2023-10-16 22:00:00+02:00 | 12509 |
| val | 2023-10-16 23:15:00+02:00 | 2023-11-13 19:00:00+01:00 | 2676 |
| test | 2023-11-13 20:15:00+01:00 | 2023-12-11 17:15:00+01:00 | 2677 |

Time-ordered, with a 1 h gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 0.459 | 0.233 | 157.278 | -9.457 | 0.511 |
| gbm | ml | 0.469 | 0.239 | 160.792 | -11.547 | 0.489 |
| ridge | ml | 0.477 | 0.284 | 163.601 | -8.025 | 0.471 |
| time_of_day_profile | baseline | 0.538 | 0.284 | 184.223 | -25.115 | 0.329 |
| persistence | baseline | 0.595 | 0.247 | 204.023 | -0.000 | 0.177 |
| same_time_yesterday | baseline | 0.745 | 0.345 | 255.435 | 4.013 | -0.290 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 7, 'base__max_iter': 100, 'base__learning_rate': 0.2, 'base__l2_regularization': 1.0}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (count) | 0.507 | 0.501 |
| MAE (count) | 0.273 | 0.259 |
| CV(RMSE) % | 133.988 | 132.534 |
| NMBE % | 0.838 | 7.270 |
| R² | 0.522 | 0.532 |

Skill vs time_of_day_profile: **-0.01** (1 = perfect, 0 = no better than the baseline).

90% prediction interval: ±0.741 count (width from validation errors); it contained 87% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2023-10-16 to 2023-11-04 | 1787 | 0.17 |
| 2023-11-04 to 2023-11-23 | 1787 | 0.01 |
| 2023-11-23 to 2023-12-11 | 1787 | 0.01 |

Pooled skill: **0.07**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 49% |
| RoomD:People__amount (recent history) | 43% |
| RoomD:Light__on_off_signal | 4% |
| RoomD:Room__active | 1% |
| Ventilation:EL_meter__power | 1% |
| RoomD:Sensor__CO2 | 1% |
| Ventilation:Fan__air_flow__supply | 1% |

> Warning: The model is barely better than time_of_day_profile on test data (skill -0.01).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
