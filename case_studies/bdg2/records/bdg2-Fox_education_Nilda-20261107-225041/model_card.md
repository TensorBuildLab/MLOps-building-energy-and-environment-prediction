# Model card: bdg2-Fox_education_Nilda

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:50:41 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `dd5d530e0ede1d54`, prepared `d95d0d158eeb82c9`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 07:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 12.6 to 257 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 08:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 11.396 | 18.103 |
| MAE (kWh) | 8.013 | 11.574 |
| CV(RMSE) % | 8.408 | 13.356 |
| NMBE % | -0.395 | -0.436 |
| R² | 0.902 | 0.753 |

Skill vs persistence: 0.37.

90% prediction interval: ±18 kWh; it contained 90% of test values.

Main inputs: electricity (recent history) (67%), calendar (time of day, weekday) (33%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.370 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 8.4%, NMBE -0.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2608 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
