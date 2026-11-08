# Model card: robod-room2-indoor_relative_humidity-30min

## Model

- **Task:** forecast indoor_relative_humidity (relative_humidity, %) 30 min ahead (2 step(s) of 15 min)
- **Model:** ridge {'model__alpha': np.float64(1.8590843630169627)}
- **Trained:** 2026-10-29T02:08:37 with bemlops 0.2.0.dev0 (code e85edf1)
- **Data fingerprint:** raw `c6a829cc3ea6a0c8`, prepared `1abacd60dc8e7f52`

## Intended use

Forecast humidity 30 min ahead (tropical climate).

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2021-09-07 00:00:00+08:00 to 2021-12-17 14:30:00+08:00 (train + validation)
- **Inputs:** `indoor_co2` (co2, ppm), `air_temperature` (zone_air_temperature, degC), `pm2.5` (pm25, ug/m3), `illuminance` (illuminance, lux), `voc` (other), `sound_pressure_level` (other), `wifi_connected_devices` (other), `occupant_count` (occupancy_count, count), `occupant_presence` (occupancy_status, binary), `plug_load_energy` (energy, kWh), `lighting_energy` (energy, kWh), `chilled_water_energy` (energy, kWh), `temp_setpoint` (temperature_setpoint, degC), `supply_air_temperature` (supply_air_temperature, degC), `dry_bulb_temp` (outdoor_air_temperature, degC), `global_horizontal_solar_radiation` (solar_irradiance, W/m2), `outdoor_relative_humidity` (relative_humidity, %)
- **Target range seen:** 45.5 to 92.7 %

## Performance (held-out test period, time-ordered)

Test period 2021-12-17 15:15:00+08:00 to 2021-12-23 23:45:00+08:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (%) | 3.978 | 3.440 |
| MAE (%) | 1.828 | 1.520 |
| CV(RMSE) % | 5.657 | 4.892 |
| NMBE % | -0.576 | -0.197 |
| R² | 0.831 | 0.874 |

Skill vs persistence: -0.16.

90% prediction interval: ±3.5 %; it contained 88% of test values.

Main inputs: indoor_relative_humidity (recent history) (97%), voc (1%), calendar (time of day, weekday) (1%).

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill -0.156 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 416 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Feb, Mar, Apr, May, Jun, Jul, Aug. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill -0.16).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
