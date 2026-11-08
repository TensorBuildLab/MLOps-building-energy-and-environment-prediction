# Model card: bdg2-Robin_education_Madeline

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:44:08 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `9d3c9370e15fa52a`, prepared `efe5571d018a3e75`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-17 16:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 81.2 to 679 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-18 17:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 15.002 | 24.048 |
| MAE (kWh) | 9.237 | 13.146 |
| CV(RMSE) % | 4.263 | 6.834 |
| NMBE % | -1.336 | -2.915 |
| R² | 0.877 | 0.683 |

Skill vs towt: 0.38.

90% prediction interval: ±18.7 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (64%), calendar (time of day, weekday) (36%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.376 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 4.3%, NMBE -1.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2251 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
