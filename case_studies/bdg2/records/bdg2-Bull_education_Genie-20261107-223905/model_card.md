# Model card: bdg2-Bull_education_Genie

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:39:05 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `f56546e76360cd5e`, prepared `31986e30e441af90`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-11 17:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 2 to 506 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 18:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 13.623 | 22.020 |
| MAE (kWh) | 5.967 | 10.735 |
| CV(RMSE) % | 10.546 | 17.047 |
| NMBE % | -0.089 | -2.082 |
| R² | 0.876 | 0.675 |

Skill vs same_time_last_week: 0.38.

90% prediction interval: ±10.5 kWh; it contained 87% of test values.

Main inputs: electricity (recent history) (74%), calendar (time of day, weekday) (25%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.381 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 10.5%, NMBE -0.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2560 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
