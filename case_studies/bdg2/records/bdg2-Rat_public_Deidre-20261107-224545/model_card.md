# Model card: bdg2-Rat_public_Deidre

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:45:45 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `fc0665a0d6a73139`, prepared `cf89ded6763cf900`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 10:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 3 to 20.3 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 11:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 1.441 | 1.692 |
| MAE (kWh) | 1.110 | 1.333 |
| CV(RMSE) % | 17.000 | 19.961 |
| NMBE % | 3.538 | 2.357 |
| R² | 0.202 | -0.100 |

Skill vs towt: 0.15.

90% prediction interval: ±2.89 kWh; it contained 96% of test values.

Main inputs: electricity (recent history) (94%), airTemperature (6%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.148 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 17.0%, NMBE 3.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2604 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
