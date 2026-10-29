# Model card: bdg2-Rat_education_Colin

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-10-29T02:42:19 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `8d21a96010943e4e`, prepared `9709137c50fa75f7`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 17:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 21.9 to 163 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 18:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 26.342 | 4.283 |
| MAE (kWh) | 21.927 | 2.268 |
| CV(RMSE) % | 134.824 | 21.921 |
| NMBE % | -110.495 | -2.843 |
| R² | -2.627 | 0.904 |

Skill vs persistence: -5.15.

90% prediction interval: ±18.1 kWh; it contained 37% of test values.

Main inputs: electricity (recent history) (66%), calendar (time of day, weekday) (13%), dewTemperature (11%), airTemperature (10%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill -5.151 vs required 0.05 |
| guideline14 | no | CV(RMSE) 134.8%, NMBE -110.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2597 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill -5.15).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
