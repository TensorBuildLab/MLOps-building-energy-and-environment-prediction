# Model card: bdg2-Hog_health_Hisako

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:47:17 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `55e26c6ce621b19f`, prepared `6967385eddab66eb`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 07:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 40.2 to 311 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 08:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 9.977 | 15.502 |
| MAE (kWh) | 6.452 | 11.947 |
| CV(RMSE) % | 5.078 | 7.890 |
| NMBE % | -1.777 | -5.803 |
| R² | 0.861 | 0.665 |

Skill vs time_of_week_profile: 0.36.

90% prediction interval: ±13.4 kWh; it contained 90% of test values.

Main inputs: electricity (recent history) (66%), calendar (time of day, weekday) (34%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.356 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 5.1%, NMBE -1.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2607 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
