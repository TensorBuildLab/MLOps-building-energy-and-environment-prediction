# Model card: bdg2-Bear_lodging_Erick

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:41:22 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `177a0baa93641593`, prepared `35b902aa64b8eb0d`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-11 23:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 13.5 to 113 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-13 00:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 5.989 | 6.174 |
| MAE (kWh) | 4.491 | 4.616 |
| CV(RMSE) % | 11.555 | 11.912 |
| NMBE % | -1.616 | 0.118 |
| R² | 0.789 | 0.776 |

Skill vs persistence: 0.03.

90% prediction interval: ±7.46 kWh; it contained 83% of test values.

Main inputs: electricity (recent history) (87%), calendar (time of day, weekday) (10%), dewTemperature (2%), windSpeed (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.030 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 11.6%, NMBE -1.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2603 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill 0.03).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
