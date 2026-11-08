# Model card: bdg2-Robin_education_Kristopher

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:38:45 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `960bdb0c5c5713fd`, prepared `349c7166391e2199`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.637 to 268 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 07:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 12.967 | 16.675 |
| MAE (kWh) | 8.702 | 11.460 |
| CV(RMSE) % | 9.962 | 12.811 |
| NMBE % | 0.447 | 6.370 |
| R² | 0.689 | 0.485 |

Skill vs towt: 0.22.

90% prediction interval: ±56.8 kWh; it contained 100% of test values.

Main inputs: electricity (recent history) (68%), calendar (time of day, weekday) (32%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.222 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 10.0%, NMBE 0.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2609 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
