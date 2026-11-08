# Model card: bdg2-Cockatoo_education_Laurence

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:48:08 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `cf5df30cf3514f9c`, prepared `dab98154158e849b`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-21 19:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 27.1 to 234 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-22 20:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 26.988 | 29.793 |
| MAE (kWh) | 18.745 | 20.749 |
| CV(RMSE) % | 35.970 | 39.708 |
| NMBE % | -0.438 | 2.079 |
| R² | 0.465 | 0.348 |

Skill vs towt: 0.09.

90% prediction interval: ±39.5 kWh; it contained 89% of test values.

Main inputs: calendar (time of day, weekday) (50%), electricity (recent history) (49%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.094 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 36.0%, NMBE -0.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2395 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
