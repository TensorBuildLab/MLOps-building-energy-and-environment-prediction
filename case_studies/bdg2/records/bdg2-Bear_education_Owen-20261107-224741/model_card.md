# Model card: bdg2-Bear_education_Owen

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:47:41 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `6f8e9fa8718e4a70`, prepared `fa7f5c1a2af663e8`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 41.3 to 270 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 16.821 | 24.104 |
| MAE (kWh) | 9.617 | 11.614 |
| CV(RMSE) % | 11.409 | 16.349 |
| NMBE % | -2.543 | -2.068 |
| R² | 0.915 | 0.825 |

Skill vs same_time_last_week: 0.30.

90% prediction interval: ±15.5 kWh; it contained 82% of test values.

Main inputs: electricity (recent history) (79%), calendar (time of day, weekday) (21%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.302 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 11.4%, NMBE -2.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2606 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
