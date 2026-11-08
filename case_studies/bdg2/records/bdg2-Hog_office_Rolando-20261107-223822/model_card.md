# Model card: bdg2-Hog_office_Rolando

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 7, 'base__max_iter': 100, 'base__learning_rate': 0.2, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:38:22 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `691bd49f9be38408`, prepared `b856980a152004b5`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 17:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 51 to 853 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 18:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 26.734 | 17.868 |
| MAE (kWh) | 14.640 | 9.510 |
| CV(RMSE) % | 6.302 | 4.212 |
| NMBE % | -2.642 | -0.258 |
| R² | -0.035 | 0.538 |

Skill vs same_time_last_week: -0.50.

90% prediction interval: ±22.1 kWh; it contained 83% of test values.

Main inputs: electricity (recent history) (50%), calendar (time of day, weekday) (33%), dewTemperature (15%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill -0.496 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 6.3%, NMBE -2.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2598 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than same_time_last_week on test data (skill -0.50).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
