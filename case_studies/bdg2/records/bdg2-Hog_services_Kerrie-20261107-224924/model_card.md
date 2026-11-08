# Model card: bdg2-Hog_services_Kerrie

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:49:24 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `8e4195f081e2b377`, prepared `3bde241d0e284981`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 5.27 to 44.7 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 2.720 | 3.079 |
| MAE (kWh) | 1.880 | 2.245 |
| CV(RMSE) % | 14.791 | 16.742 |
| NMBE % | -2.401 | -5.846 |
| R² | 0.689 | 0.601 |

Skill vs towt: 0.12.

90% prediction interval: ±5.45 kWh; it contained 94% of test values.

Main inputs: calendar (time of day, weekday) (58%), electricity (recent history) (42%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.117 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 14.8%, NMBE -2.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2607 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
