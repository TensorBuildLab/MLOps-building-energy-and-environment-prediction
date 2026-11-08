# Model card: bdg2-Bull_education_Roseann

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:44:26 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `8391823145e3b9e5`, prepared `8e2b4cf03c9be548`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-12 09:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 4 to 1.26e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-13 10:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 27.170 | 36.199 |
| MAE (kWh) | 9.948 | 14.092 |
| CV(RMSE) % | 10.979 | 14.627 |
| NMBE % | -1.634 | -1.837 |
| R² | 0.406 | -0.055 |

Skill vs same_time_last_week: 0.25.

90% prediction interval: ±8.16 kWh; it contained 69% of test values.

Main inputs: electricity (recent history) (74%), calendar (time of day, weekday) (25%), windSpeed (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.249 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 11.0%, NMBE -1.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2545 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
