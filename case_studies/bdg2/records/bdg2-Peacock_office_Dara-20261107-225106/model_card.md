# Model card: bdg2-Peacock_office_Dara

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:51:06 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `134ec380c9a8f59d`, prepared `6059c2aeb815a87a`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 12:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 45.8 to 341 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 13:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 26.510 | 33.492 |
| MAE (kWh) | 20.064 | 24.960 |
| CV(RMSE) % | 14.977 | 18.922 |
| NMBE % | 2.201 | 0.171 |
| R² | 0.834 | 0.735 |

Skill vs persistence: 0.21.

90% prediction interval: ±43.5 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (78%), calendar (time of day, weekday) (22%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.208 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 15.0%, NMBE 2.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2603 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
