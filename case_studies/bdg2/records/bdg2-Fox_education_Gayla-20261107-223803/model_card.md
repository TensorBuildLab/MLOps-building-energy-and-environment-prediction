# Model card: bdg2-Fox_education_Gayla

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:38:03 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `513c1ea825ece5d3`, prepared `f265e1d1613a6e62`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-20 21:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 8.82 to 131 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-21 22:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 10.452 | 14.912 |
| MAE (kWh) | 7.512 | 11.033 |
| CV(RMSE) % | 18.022 | 25.713 |
| NMBE % | -3.811 | -7.344 |
| R² | 0.825 | 0.644 |

Skill vs time_of_week_profile: 0.30.

90% prediction interval: ±12 kWh; it contained 81% of test values.

Main inputs: electricity (recent history) (71%), calendar (time of day, weekday) (28%), dewTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.299 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 18.0%, NMBE -3.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2424 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
