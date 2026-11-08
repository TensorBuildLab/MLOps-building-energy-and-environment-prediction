# Model card: bdg2-Fox_education_Elvira

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:46:19 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `cc05ca276fbe5c50`, prepared `be96c81ba467514c`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 10:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 26.6 to 427 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 11:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 18.128 | 24.277 |
| MAE (kWh) | 11.909 | 15.026 |
| CV(RMSE) % | 10.283 | 13.771 |
| NMBE % | 0.617 | 1.041 |
| R² | 0.874 | 0.773 |

Skill vs same_time_last_week: 0.25.

90% prediction interval: ±16.6 kWh; it contained 78% of test values.

Main inputs: electricity (recent history) (79%), calendar (time of day, weekday) (20%), dewTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.253 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 10.3%, NMBE 0.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2605 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
