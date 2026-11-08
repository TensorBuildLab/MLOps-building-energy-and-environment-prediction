# Model card: bdg2-Wolf_education_Arnulfo

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:44:23 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `add9926fcd36da6a`, prepared `72c6c112c37af400`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-15 14:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 12.7 to 98.7 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-16 15:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 10.812 | 16.068 |
| MAE (kWh) | 7.216 | 9.635 |
| CV(RMSE) % | 28.621 | 42.536 |
| NMBE % | -1.977 | -0.231 |
| R² | 0.617 | 0.154 |

Skill vs persistence: 0.33.

90% prediction interval: ±21.2 kWh; it contained 94% of test values.

Main inputs: calendar (time of day, weekday) (56%), electricity (recent history) (43%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.327 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 28.6%, NMBE -2.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2552 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
