# Model card: bdg2-Robin_office_Lindsay

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:42:11 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `e2efb30df8f27a9c`, prepared `31b2d5bf64375a16`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-07 10:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 3.94 to 135 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-08 11:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 9.119 | 7.270 |
| MAE (kWh) | 7.239 | 5.205 |
| CV(RMSE) % | 15.298 | 12.197 |
| NMBE % | -9.545 | 2.781 |
| R² | 0.651 | 0.778 |

Skill vs same_time_last_week: -0.25.

90% prediction interval: ±9.33 kWh; it contained 69% of test values.

Main inputs: electricity (recent history) (58%), calendar (time of day, weekday) (39%), dewTemperature (3%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill -0.254 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 15.3%, NMBE -9.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2479 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than same_time_last_week on test data (skill -0.25).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
