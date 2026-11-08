# Model card: bdg2-Cockatoo_public_Leah

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:40:46 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `8c7cb6e241b94ff6`, prepared `7920a8328014ed05`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-21 19:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 66.7 to 264 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-22 20:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 11.589 | 30.493 |
| MAE (kWh) | 8.400 | 18.144 |
| CV(RMSE) % | 6.987 | 18.383 |
| NMBE % | -0.917 | -3.355 |
| R² | 0.915 | 0.408 |

Skill vs towt: 0.62.

90% prediction interval: ±13.8 kWh; it contained 83% of test values.

Main inputs: electricity (recent history) (68%), calendar (time of day, weekday) (30%), dewTemperature (1%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.620 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 7.0%, NMBE -0.9% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2395 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
