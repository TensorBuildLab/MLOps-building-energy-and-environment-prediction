# Run report: aalborg-roomf-room-active-1h

**Task:** forecast yes/no RoomF:Room__active (occupancy_status, binary) 1 h ahead (4 step(s) of 15 min)

## Data check

88705 raw rows from 2023-02-27 00:00:00+01:00 to 2024-01-01 00:00:00+01:00, typical step 5 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `columns:undeclared` | 167 column(s) are not declared and will be ignored: Heating:Control__setpoint_water_temperature__supply, Heating:DH__energy_accumulated, Heating:DH__operation_hours_accumulated, Heating:DH__water_flow, Heating:DH__water_flow_accumulated, Heating:DH__water_temperature__return, Heating:DH__water_temperature__supply, Heating:Mixing_valve__control_signal .... | Declare any you want the model to use. |
| warning | `stuck:Outdoor:Temperature_air` | Sensor repeats exactly 4.99997 for 1 d 13 h 15 min (2023-11-19 06:15:00+01:00 to 2023-11-20 19:30:00+01:00); 60 such stretch(es), 26 d 10 h 30 min in total. | prepare() treats these stretches as missing. |
| warning | `stuck:Outdoor:Wind__velocity` | Sensor repeats exactly 0.64299 for 1 d 1 h 20 min (2023-02-28 11:15:00+01:00 to 2023-03-01 12:35:00+01:00); 116 such stretch(es), 46 d 3 h 20 min in total. The value is unchanged in 82% of steps and changes by at least ~0.20278 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `spikes:Outdoor:Wind__velocity` | 289 single-sample spike(s), e.g. 4.20511, 4.61631, 4.64302 at 2023-03-23 11:10:00+01:00. | prepare() treats them as missing. |
| warning | `spikes:RoomF:Sensor__CO2` | 319 single-sample spike(s), e.g. 664, 764, 567 at 2023-02-27 12:50:00+01:00. | prepare() treats them as missing. |
| warning | `spikes:RoomF:Sensor__room_temperature` | 39 single-sample spike(s), e.g. 22.97, 22.61, 22.31 at 2023-03-01 04:55:00+01:00. | prepare() treats them as missing. |
| warning | `missing:RoomF:People__amount` | 43% of entries are missing. | Models that need complete inputs fill them with the training median. |

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
- mask_spikes `RoomF:Sensor__CO2`: Single-sample spikes set to missing. (319)
- mask_spikes `RoomF:Sensor__room_temperature`: Single-sample spikes set to missing. (39)
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
- forward_fill `RoomF:Sensor__CO2`: Filled input gaps up to 1h with the last known value. (11)
- forward_fill `RoomF:Sensor__room_temperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `RoomF:People__amount`: Filled input gaps up to 1h with the last known value. (90)
- forward_fill `RoomF:Damper__position`: Filled input gaps up to 1h with the last known value. (2)
- forward_fill `RoomF:Radiator__control_signal__motor_valve`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `RoomF:Light__level__ceiling`: Filled input gaps up to 1h with the last known value. (2)
- forward_fill `RoomF:Light__on_off_signal`: Filled input gaps up to 1h with the last known value. (2)
- forward_fill `RoomF:Window__opened_closed`: Filled input gaps up to 1h with the last known value. (2)
- forward_fill `RoomF:Control__setpoint_temperature_global`: Filled input gaps up to 1h with the last known value. (2)
- forward_fill `RoomF:Control__heating_limit`: Filled input gaps up to 1h with the last known value. (2)
- forward_fill `RoomF:Control__cooling_limit`: Filled input gaps up to 1h with the last known value. (2)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2023-02-27 01:00:00+01:00 | 2023-09-30 15:30:00+02:00 | 20694 |
| val | 2023-09-30 16:45:00+02:00 | 2023-11-15 19:00:00+01:00 | 4430 |
| test | 2023-11-15 20:15:00+01:00 | 2024-01-01 00:00:00+01:00 | 4432 |

Time-ordered, with a 1 h gap between sets.

## Validation

| model | type | Brier score | Accuracy | Balanced accuracy | F1 | ROC AUC |
|---|---|---|---|---|---|---|
| logistic | ml | 0.058 | 0.920 | 0.840 | 0.736 | 0.961 |
| gbm | ml | 0.060 | 0.916 | 0.860 | 0.742 | 0.959 |
| persistence | baseline | 0.087 | 0.907 | 0.823 | 0.700 | 0.839 |
| same_time_yesterday | baseline | 0.171 | 0.821 | 0.650 | 0.410 | 0.663 |

## Test result

Chosen model: **logistic** {'model__C': np.float64(1.96282248134428)}

| Metric | Model | persistence |
|---|---|---|
| Brier score | 0.048 | 0.063 |
| Accuracy | 0.934 | 0.933 |
| Balanced accuracy | 0.910 | 0.849 |
| F1 | 0.774 | 0.737 |
| ROC AUC | 0.972 | 0.872 |

Skill vs persistence: **0.24** (1 = perfect, 0 = no better than the baseline).

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2023-09-30 to 2023-10-31 | 2957 | 0.36 |
| 2023-10-31 to 2023-12-01 | 2957 | 0.28 |
| 2023-12-01 to 2024-01-01 | 2956 | 0.24 |

Pooled skill: **0.30**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 55% |
| RoomF:Room__active (recent history) | 35% |
| RoomF:Control__heating_limit | 4% |
| Outdoor:Temperature_air | 3% |
| RoomF:Light__level__ceiling | 1% |
| Heating:DH__power | 1% |

## Plots

![timeseries](test_timeseries.png)
