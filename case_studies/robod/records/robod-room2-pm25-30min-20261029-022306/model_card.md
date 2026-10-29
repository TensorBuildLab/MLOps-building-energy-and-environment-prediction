# Model card: robod-room2-pm25-30min

## Model

- **Task:** forecast pm2.5 (pm25, ug/m3) 30 min ahead (2 step(s) of 15 min)
- **Model:** ridge {'model__alpha': np.float64(0.348280208702833)}
- **Trained:** 2026-10-29T02:23:06 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `c6a829cc3ea6a0c8`, prepared `4d45a63543f859dc`

## Intended use

Forecast PM2.5 30 min ahead.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 14:45:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `indoor_relative_humidity` (relative_humidity, %), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 0.18 to 179 ug/m3

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 15:30:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (ug/m3) | 13.036 | 16.115 |
| MAE (ug/m3) | 6.102 | 6.165 |
| CV(RMSE) % | 104.176 | 128.777 |
| NMBE % | 18.674 | 1.758 |
| R² | 0.541 | 0.298 |

Skill vs persistence: 0.19.

90% prediction interval: ±7.03 ug/m3; it contained 79% of test values.

Main inputs: pm2.5 (recent history) (97%), indoor_co2 (2%), dry_bulb_temp (1%), sound_pressure_level (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.191 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 416 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
