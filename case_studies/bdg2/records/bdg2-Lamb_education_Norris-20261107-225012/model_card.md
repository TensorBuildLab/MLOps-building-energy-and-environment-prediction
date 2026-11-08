# Model card: bdg2-Lamb_education_Norris

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:50:12 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `07e7cc223adc8e11`, prepared `cad47b6c2c7fe741`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-20 01:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.0003 to 60.6 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-21 02:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 2.853 | 4.142 |
| MAE (kWh) | 2.025 | 1.922 |
| CV(RMSE) % | 44.541 | 64.674 |
| NMBE % | -17.231 | -7.412 |
| R² | 0.809 | 0.597 |

Skill vs same_time_last_week: 0.31.

90% prediction interval: ±4.48 kWh; it contained 90% of test values.

Main inputs: electricity (recent history) (61%), calendar (time of day, weekday) (38%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.311 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 44.5%, NMBE -17.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2441 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
