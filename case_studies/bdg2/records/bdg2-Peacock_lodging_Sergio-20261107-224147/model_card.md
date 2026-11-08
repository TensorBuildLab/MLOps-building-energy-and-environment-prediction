# Model card: bdg2-Peacock_lodging_Sergio

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:41:47 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `d32de608654719a7`, prepared `c1b2cc4bf2b9ad51`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 51 to 174 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 12.261 | 14.061 |
| MAE (kWh) | 8.951 | 9.996 |
| CV(RMSE) % | 13.260 | 15.207 |
| NMBE % | -2.948 | -0.227 |
| R² | 0.639 | 0.525 |

Skill vs persistence: 0.13.

90% prediction interval: ±15.7 kWh; it contained 83% of test values.

Main inputs: electricity (recent history) (86%), calendar (time of day, weekday) (14%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.128 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 13.3%, NMBE -2.9% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2607 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
