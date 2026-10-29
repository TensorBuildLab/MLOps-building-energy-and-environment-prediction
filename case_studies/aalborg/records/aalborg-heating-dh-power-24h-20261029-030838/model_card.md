# Model card: aalborg-heating-dh-power-24h

## Model

- **Task:** forecast Heating:DH__power (thermal_power, kW) 1 d ahead (96 step(s) of 15 min)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-10-29T03:08:38 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `735e35c55fccbd76`, prepared `23464cf3808e94e2`

## Intended use

Forecast district-heating power a day ahead (no weather forecast used).

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 01:00:00+01:00 to 2023-11-15 19:00:00+01:00 (train + validation)
- **Inputs:** `Outdoor:Temperature_air` (outdoor_air_temperature, degC), `Outdoor:Wind__velocity` (wind_speed, m/s), `Outdoor:Solar__direct_radiation__east_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__south_façade` (solar_irradiance, W/m2), `Outdoor:Solar__direct_radiation__west_façade` (solar_irradiance, W/m2), `Ventilation:EL_meter__power` (electric_power, W), `Ventilation:Fan__air_flow__supply` (airflow, m3/h), `Ventilation:Sensor__air_temperature__supply` (supply_air_temperature, degC), `Ventilation:HC__power` (thermal_power, W)
- **Target range seen:** 0 to 29.3 kW

## Performance (held-out test period, time-ordered)

Test period 2023-11-16 19:15:00+01:00 to 2024-01-01 00:00:00+01:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kW) | 4.227 | 4.804 |
| MAE (kW) | 3.106 | 3.565 |
| CV(RMSE) % | 33.335 | 37.882 |
| NMBE % | 3.221 | 0.542 |
| R² | 0.372 | 0.189 |

Skill vs persistence: 0.12.

90% prediction interval: ±1.24 kW; it contained 28% of test values.

Main inputs: Heating:DH__power (recent history) (97%), calendar (time of day, weekday) (2%), Ventilation:Fan__air_flow__supply (1%), Ventilation:HC__power (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.120 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 27.4%, NMBE 3.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 4340 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
