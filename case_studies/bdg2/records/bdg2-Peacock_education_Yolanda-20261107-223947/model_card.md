# Model card: bdg2-Peacock_education_Yolanda

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:39:47 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `e6dfbb3ecfd7d2e6`, prepared `63177335596d5c91`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 23.2 to 58.8 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 2.095 | 3.551 |
| MAE (kWh) | 1.443 | 2.438 |
| CV(RMSE) % | 6.092 | 10.327 |
| NMBE % | -1.315 | -0.453 |
| R² | 0.914 | 0.752 |

Skill vs same_time_last_week: 0.41.

90% prediction interval: ±3.39 kWh; it contained 93% of test values.

Main inputs: electricity (recent history) (76%), calendar (time of day, weekday) (23%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.410 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 6.1%, NMBE -1.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2607 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
