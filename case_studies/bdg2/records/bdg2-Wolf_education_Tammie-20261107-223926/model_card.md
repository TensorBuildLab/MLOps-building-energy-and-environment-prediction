# Model card: bdg2-Wolf_education_Tammie

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:39:26 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `ca5e45b18a2951a3`, prepared `883653ce07367215`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 15.4 to 145 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 07:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 10.595 | 14.825 |
| MAE (kWh) | 7.036 | 10.166 |
| CV(RMSE) % | 12.856 | 17.989 |
| NMBE % | 0.365 | -0.687 |
| R² | 0.811 | 0.630 |

Skill vs time_of_day_profile: 0.29.

90% prediction interval: ±17.8 kWh; it contained 91% of test values.

Main inputs: calendar (time of day, weekday) (52%), electricity (recent history) (48%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.285 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 12.9%, NMBE 0.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2608 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
