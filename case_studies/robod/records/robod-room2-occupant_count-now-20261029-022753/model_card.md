# Model card: robod-room2-occupant_count-now

## Model

- **Task:** estimate occupant_count (occupancy_count, count) at the same moment as its inputs (estimation / virtual sensor)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-10-29T02:27:53 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `c6a829cc3ea6a0c8`, prepared `d98ec9646fcb7e5d`

## Intended use

Estimate the number of people now from Wi-Fi, CO2, sound and plug loads (virtual people counter).

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 15:00:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0 to 22 count

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 15:15:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (count) | 2.968 | 4.669 |
| MAE (count) | 1.614 | 2.169 |
| CV(RMSE) % | 145.578 | 228.979 |
| NMBE % | -8.139 | 45.241 |
| R² | 0.673 | 0.192 |

Skill vs time_of_day_profile: 0.36.

90% prediction interval: ±4.36 count; it contained 84% of test values.

Main inputs: wifi_connected_devices (94%), outdoor_relative_humidity (3%), dry_bulb_temp (2%), chilled_water_energy (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.364 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 419 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
