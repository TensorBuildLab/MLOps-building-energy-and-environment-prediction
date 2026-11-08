# Model card: bdg2-Bobcat_office_Nikita

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:43:57 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `72ae279476461ce5`, prepared `752b0d6207889c32`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-20 15:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 3.75 to 119 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-21 16:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 5.294 | 6.336 |
| MAE (kWh) | 3.400 | 3.257 |
| CV(RMSE) % | 16.401 | 19.627 |
| NMBE % | -5.915 | -1.216 |
| R² | 0.744 | 0.633 |

Skill vs same_time_last_week: 0.16.

90% prediction interval: ±15 kWh; it contained 98% of test values.

Main inputs: calendar (time of day, weekday) (50%), electricity (recent history) (49%), dewTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.164 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 16.4%, NMBE -5.9% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2429 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
