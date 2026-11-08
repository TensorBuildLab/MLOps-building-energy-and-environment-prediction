# Model card: bdg2-Wolf_education_Cody

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 7, 'base__max_iter': 100, 'base__learning_rate': 0.2, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:38:22 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `345360ee13a23e78`, prepared `0776516f92f46f7e`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1.59 to 137 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 21.773 | 23.105 |
| MAE (kWh) | 14.960 | 15.359 |
| CV(RMSE) % | 82.009 | 87.026 |
| NMBE % | -4.951 | 9.859 |
| R² | 0.370 | 0.290 |

Skill vs time_of_day_profile: 0.06.

90% prediction interval: ±32.9 kWh; it contained 89% of test values.

Main inputs: calendar (time of day, weekday) (67%), electricity (recent history) (32%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.058 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 82.0%, NMBE -5.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2606 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
