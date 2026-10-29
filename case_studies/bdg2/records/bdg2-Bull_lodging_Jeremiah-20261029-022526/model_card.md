# Model card: bdg2-Bull_lodging_Jeremiah

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-10-29T02:25:26 with bemlops 0.2.0.dev0 (code 57824a1)
- **Data fingerprint:** raw `fc3e06af006852f4`, prepared `14b5bfe52fc21101`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-11 19:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 6 to 245 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 20:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 8.326 | 15.936 |
| MAE (kWh) | 4.599 | 8.974 |
| CV(RMSE) % | 12.986 | 24.855 |
| NMBE % | 0.849 | -0.684 |
| R² | 0.834 | 0.393 |

Skill vs persistence: 0.48.

90% prediction interval: ±9.3 kWh; it contained 89% of test values.

Main inputs: electricity (recent history) (66%), calendar (time of day, weekday) (33%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.478 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 13.0%, NMBE 0.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2558 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
