# Model card: bdg2-Moose_education_Marina

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:40:45 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `53a56143ae460a8f`, prepared `3bf88bc567543009`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-19 20:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 16.7 to 93.6 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-20 21:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 4.315 | 5.730 |
| MAE (kWh) | 2.987 | 3.997 |
| CV(RMSE) % | 10.565 | 14.027 |
| NMBE % | -0.313 | 0.180 |
| R² | 0.770 | 0.594 |

Skill vs same_time_last_week: 0.25.

90% prediction interval: ±4.53 kWh; it contained 79% of test values.

Main inputs: electricity (recent history) (68%), calendar (time of day, weekday) (31%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.247 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 10.6%, NMBE -0.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2425 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
