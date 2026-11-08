# Model card: bdg2-Wolf_education_Tori

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:48:42 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `02807aafc962bdde`, prepared `ef6d1bef0747463a`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 87.2 to 796 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 07:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 72.774 | 82.283 |
| MAE (kWh) | 51.467 | 61.265 |
| CV(RMSE) % | 20.850 | 23.575 |
| NMBE % | -8.325 | -9.365 |
| R² | 0.621 | 0.516 |

Skill vs time_of_day_profile: 0.12.

90% prediction interval: ±124 kWh; it contained 90% of test values.

Main inputs: calendar (time of day, weekday) (65%), electricity (recent history) (34%), dewTemperature (1%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.116 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 20.9%, NMBE -8.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2608 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
