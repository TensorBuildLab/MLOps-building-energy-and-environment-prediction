# Model card: bdg2-Bear_education_Destiny

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:40:04 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `5cffa50d092f7972`, prepared `28cd14fc7ccf1015`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-23 03:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 47 to 317 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-24 04:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 15.404 | 21.611 |
| MAE (kWh) | 11.195 | 14.521 |
| CV(RMSE) % | 15.240 | 21.381 |
| NMBE % | -4.149 | -0.282 |
| R² | 0.867 | 0.739 |

Skill vs persistence: 0.29.

90% prediction interval: ±29.1 kWh; it contained 94% of test values.

Main inputs: electricity (recent history) (78%), calendar (time of day, weekday) (22%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.287 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 15.2%, NMBE -4.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2372 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
