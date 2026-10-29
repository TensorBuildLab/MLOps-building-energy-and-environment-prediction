# Run report: aalborg-heating-dh-power-24h

**Task:** forecast Heating:DH__power (thermal_power, kW) 1 d ahead (96 step(s) of 15 min)

## Data check

88705 raw rows from 2023-02-27 00:00:00+01:00 to 2024-01-01 00:00:00+01:00, typical step 5 min.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `columns:undeclared` | 179 column(s) are not declared and will be ignored: Heating:Control__setpoint_water_temperature__supply, Heating:DH__energy_accumulated, Heating:DH__operation_hours_accumulated, Heating:DH__water_flow, Heating:DH__water_flow_accumulated, Heating:DH__water_temperature__return, Heating:DH__water_temperature__supply, Heating:Mixing_valve__control_signal .... | Declare any you want the model to use. |
| warning | `stuck:Outdoor:Temperature_air` | Sensor repeats exactly 4.99997 for 1 d 13 h 15 min (2023-11-19 06:15:00+01:00 to 2023-11-20 19:30:00+01:00); 60 such stretch(es), 26 d 10 h 30 min in total. | prepare() treats these stretches as missing. |
| warning | `stuck:Outdoor:Wind__velocity` | Sensor repeats exactly 0.64299 for 1 d 1 h 20 min (2023-02-28 11:15:00+01:00 to 2023-03-01 12:35:00+01:00); 116 such stretch(es), 46 d 3 h 20 min in total. The value is unchanged in 82% of steps and changes by at least ~0.20278 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `spikes:Outdoor:Wind__velocity` | 289 single-sample spike(s), e.g. 4.20511, 4.61631, 4.64302 at 2023-03-23 11:10:00+01:00. | prepare() treats them as missing. |

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
- resample: Resampled to a regular 15 min grid (29569 rows). (29569)
- forward_fill `Outdoor:Temperature_air`: Filled input gaps up to 1h with the last known value. (279)
- forward_fill `Outdoor:Wind__velocity`: Filled input gaps up to 1h with the last known value. (379)
- forward_fill `Outdoor:Solar__direct_radiation__east_façade`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Outdoor:Solar__direct_radiation__south_façade`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Outdoor:Solar__direct_radiation__west_façade`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Ventilation:EL_meter__power`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Ventilation:Fan__air_flow__supply`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Ventilation:Sensor__air_temperature__supply`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `Ventilation:HC__power`: Filled input gaps up to 1h with the last known value. (1)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2023-02-27 01:00:00+01:00 | 2023-09-30 15:30:00+02:00 | 20694 |
| val | 2023-10-01 15:45:00+02:00 | 2023-11-15 19:00:00+01:00 | 4338 |
| test | 2023-11-16 19:15:00+01:00 | 2024-01-01 00:00:00+01:00 | 4340 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 0.787 | 0.580 | 33.857 | -0.826 | 0.637 |
| gbm_change | ml | 0.811 | 0.590 | 34.892 | 3.297 | 0.615 |
| gbm | ml | 0.812 | 0.597 | 34.940 | 2.144 | 0.614 |
| persistence | baseline | 0.906 | 0.661 | 38.966 | 3.484 | 0.520 |
| same_time_yesterday | baseline | 0.906 | 0.661 | 38.966 | 3.484 | 0.520 |
| time_of_day_profile | baseline | 1.365 | 1.138 | 58.729 | -11.234 | -0.091 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kW) | 4.227 | 4.804 |
| MAE (kW) | 3.106 | 3.565 |
| CV(RMSE) % | 33.335 | 37.882 |
| NMBE % | 3.221 | 0.542 |
| R² | 0.372 | 0.189 |

Skill vs persistence: **0.12** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 27.4% (limit 30%), NMBE 3.2% (limit ±10%): **passes**.

90% prediction interval: ±1.24 kW (width from validation errors); it contained 28% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2023-09-30 to 2023-10-31 | 2957 | 0.11 |
| 2023-10-31 to 2023-12-01 | 2957 | 0.09 |
| 2023-12-01 to 2024-01-01 | 2956 | 0.14 |

Pooled skill: **0.12**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| Heating:DH__power (recent history) | 97% |
| calendar (time of day, weekday) | 2% |
| Ventilation:Fan__air_flow__supply | 1% |
| Ventilation:HC__power | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
