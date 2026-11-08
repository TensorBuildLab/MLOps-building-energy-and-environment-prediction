# Model card: bdg2-Eagle_education_Wesley

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:42:22 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `0155f997f17c2f57`, prepared `d199e8bef6bd65dd`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-14 22:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 42 to 281 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-15 23:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 13.688 | 21.720 |
| MAE (kWh) | 9.764 | 14.591 |
| CV(RMSE) % | 10.837 | 17.196 |
| NMBE % | 1.836 | -0.590 |
| R² | 0.905 | 0.760 |

Skill vs same_time_last_week: 0.37.

90% prediction interval: ±22 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (88%), calendar (time of day, weekday) (12%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.370 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 10.8%, NMBE 1.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2567 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
