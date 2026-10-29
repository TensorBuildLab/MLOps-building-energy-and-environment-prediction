# Model card: co2_forecast_1h_roomB

## Model

- **Task:** forecast co2 (co2, ppm) 1 h ahead (4 step(s) of 15 min)
- **Model:** persistence 
- **Trained:** 2026-10-29T00:21:28 with bemlops 0.1.0.dev0 (code 5c575a6)
- **Data fingerprint:** raw `13582152e8241508`, prepared `32127726b083e720`

## Intended use

1 h ahead CO2 forecast for ventilation planning

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2023-02-27 01:00:00 to 2023-05-17 23:15:00 (train + validation)
- **Inputs:** `oat` (outdoor_air_temperature, degC), `rt` (zone_air_temperature, degC), `active` (occupancy_status, binary), `light` (equipment_status, binary), `flow` (airflow, m3/h), `damper` (position, %), `sol` (solar_irradiance, W/m2)
- **Target range seen:** 382 to 1.02e+03 ppm

## Performance (held-out test period, time-ordered)

Test period 2023-05-18 00:30:00 to 2023-05-31 23:45:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (ppm) | 29.470 | 29.470 |
| MAE (ppm) | 12.448 | 12.448 |
| CV(RMSE) % | 6.333 | 6.333 |
| NMBE % | -0.010 | -0.010 |
| R² | 0.736 | 0.736 |

Skill vs persistence: 0.00.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | not applicable |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 1342 test rows (need 200) |

## Limitations

- Months not seen in training: Jan, Jun, Jul, Aug, Sep, Oct, Nov, Dec. Expect lower accuracy then; monitor closely.
- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
