# Model card: bdg2-Robin_lodging_Celia

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:47:41 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `daf5f8ab8f9fd77f`, prepared `39d5f2b8e6770b5a`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.386 to 126 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 07:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 4.979 | 6.399 |
| MAE (kWh) | 3.575 | 4.416 |
| CV(RMSE) % | 9.193 | 11.814 |
| NMBE % | -0.441 | 0.199 |
| R² | 0.936 | 0.894 |

Skill vs persistence: 0.22.

90% prediction interval: ±6.35 kWh; it contained 84% of test values.

Main inputs: electricity (recent history) (92%), calendar (time of day, weekday) (8%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.222 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 9.2%, NMBE -0.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2609 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
