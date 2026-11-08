# Model card: bdg2-Bobcat_education_Coleman

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:41:39 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `046ec5a44233613d`, prepared `6d0b0e9983157ea5`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-21 16:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 2.5 to 389 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-22 17:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 18.562 | 19.943 |
| MAE (kWh) | 11.022 | 15.092 |
| CV(RMSE) % | 15.999 | 17.189 |
| NMBE % | 2.293 | -4.999 |
| R² | 0.827 | 0.800 |

Skill vs time_of_week_profile: 0.07.

90% prediction interval: ±26.7 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (71%), calendar (time of day, weekday) (29%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.069 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 16.0%, NMBE 2.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2401 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
