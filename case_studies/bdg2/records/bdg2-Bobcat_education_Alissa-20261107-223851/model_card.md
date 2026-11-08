# Model card: bdg2-Bobcat_education_Alissa

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:38:51 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `d4e599908aabb901`, prepared `875db866fde6ac22`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-19 16:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 3 to 404 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-20 17:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 10.405 | 11.072 |
| MAE (kWh) | 6.468 | 6.900 |
| CV(RMSE) % | 17.362 | 18.475 |
| NMBE % | -3.252 | -5.347 |
| R² | 0.775 | 0.745 |

Skill vs towt: 0.06.

90% prediction interval: ±11 kWh; it contained 83% of test values.

Main inputs: electricity (recent history) (63%), calendar (time of day, weekday) (36%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.060 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 17.4%, NMBE -3.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2453 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
