# Model card: bdg2-Crow_education_Keisha

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:38:07 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `a94a3087eb90a3ca`, prepared `75df5e0d1b68ddf6`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-07-31 05:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 10.2 to 462 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-08-01 06:00:00 to 2017-11-10 00:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 13.571 | 18.814 |
| MAE (kWh) | 9.278 | 12.386 |
| CV(RMSE) % | 4.523 | 6.270 |
| NMBE % | 0.805 | 0.874 |
| R² | 0.930 | 0.865 |

Skill vs same_time_last_week: 0.28.

90% prediction interval: ±18.7 kWh; it contained 89% of test values.

Main inputs: electricity (recent history) (83%), calendar (time of day, weekday) (17%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.279 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 4.5%, NMBE 0.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2418 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
