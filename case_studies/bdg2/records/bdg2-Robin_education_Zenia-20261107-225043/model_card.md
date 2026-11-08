# Model card: bdg2-Robin_education_Zenia

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:50:43 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `3a36bbe366214b00`, prepared `a893308cd3ace57f`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-23 17:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 52.2 to 466 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-24 18:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 9.118 | 14.566 |
| MAE (kWh) | 6.734 | 9.529 |
| CV(RMSE) % | 4.239 | 6.772 |
| NMBE % | -0.206 | -1.535 |
| R² | 0.947 | 0.864 |

Skill vs same_time_last_week: 0.37.

90% prediction interval: ±23.8 kWh; it contained 98% of test values.

Main inputs: electricity (recent history) (65%), calendar (time of day, weekday) (35%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.374 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 4.2%, NMBE -0.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2358 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
