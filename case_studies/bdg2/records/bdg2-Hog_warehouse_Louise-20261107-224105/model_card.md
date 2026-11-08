# Model card: bdg2-Hog_warehouse_Louise

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:41:05 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `97a3d920bdd4b293`, prepared `897988d3cc17f6ff`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 09:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 2 to 44 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 10:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 3.277 | 4.645 |
| MAE (kWh) | 2.339 | 3.698 |
| CV(RMSE) % | 29.100 | 41.241 |
| NMBE % | -1.011 | -10.501 |
| R² | 0.865 | 0.729 |

Skill vs towt: 0.29.

90% prediction interval: ±6.02 kWh; it contained 93% of test values.

Main inputs: electricity (recent history) (58%), calendar (time of day, weekday) (40%), airTemperature (3%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.294 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 29.1%, NMBE -1.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2581 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
