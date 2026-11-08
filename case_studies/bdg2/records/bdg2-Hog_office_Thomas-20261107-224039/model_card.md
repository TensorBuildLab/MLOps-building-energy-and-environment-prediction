# Model card: bdg2-Hog_office_Thomas

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:40:39 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `490a4ba39b5cf342`, prepared `9c059668fddbc113`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-08-13 13:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 2 to 278 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-08-14 14:00:00 to 2017-11-29 09:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 27.024 | 27.558 |
| MAE (kWh) | 18.530 | 11.825 |
| CV(RMSE) % | 110.996 | 113.189 |
| NMBE % | -32.528 | -7.327 |
| R² | 0.528 | 0.510 |

Skill vs same_time_last_week: 0.02.

90% prediction interval: ±20.7 kWh; it contained 61% of test values.

Main inputs: electricity (recent history) (80%), calendar (time of day, weekday) (19%), windSpeed (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.019 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 111.0%, NMBE -32.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2455 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than same_time_last_week on test data (skill 0.02).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
