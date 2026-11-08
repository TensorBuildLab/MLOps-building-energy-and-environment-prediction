# Model card: bdg2-Eagle_office_Freida

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:48:03 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `a778f531ab6ce78c`, prepared `5260ee3d4f45d299`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-07 09:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 27 to 118 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-08 10:00:00 to 2017-12-23 03:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 6.029 | 7.977 |
| MAE (kWh) | 4.083 | 5.395 |
| CV(RMSE) % | 11.721 | 15.508 |
| NMBE % | -0.573 | 0.158 |
| R² | 0.825 | 0.693 |

Skill vs same_time_last_week: 0.24.

90% prediction interval: ±6.82 kWh; it contained 83% of test values.

Main inputs: electricity (recent history) (80%), calendar (time of day, weekday) (20%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.244 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 11.7%, NMBE -0.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2536 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
