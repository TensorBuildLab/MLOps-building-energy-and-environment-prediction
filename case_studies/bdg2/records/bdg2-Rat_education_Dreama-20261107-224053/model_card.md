# Model card: bdg2-Rat_education_Dreama

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:40:53 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `8545441efb0e72e0`, prepared `3dba581d68f117ee`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-08-30 12:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.24 to 171 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-08-31 13:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 12.523 | 12.970 |
| MAE (kWh) | 5.870 | 5.703 |
| CV(RMSE) % | 13.978 | 14.477 |
| NMBE % | 1.438 | 1.002 |
| R² | 0.591 | 0.561 |

Skill vs persistence: 0.03.

90% prediction interval: ±36 kWh; it contained 99% of test values.

Main inputs: electricity (recent history) (97%), calendar (time of day, weekday) (2%), dewTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.034 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 14.0%, NMBE 1.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2549 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill 0.03).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
