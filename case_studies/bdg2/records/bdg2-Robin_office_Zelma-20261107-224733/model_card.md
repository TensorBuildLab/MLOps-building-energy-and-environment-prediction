# Model card: bdg2-Robin_office_Zelma

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:47:33 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `cbba6744c80c5e60`, prepared `1773242046d0c056`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-24 01:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 29.7 to 204 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-25 02:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 6.854 | 13.216 |
| MAE (kWh) | 4.734 | 7.644 |
| CV(RMSE) % | 7.201 | 13.886 |
| NMBE % | -0.096 | -2.397 |
| R² | 0.959 | 0.849 |

Skill vs same_time_last_week: 0.48.

90% prediction interval: ±12.8 kWh; it contained 94% of test values.

Main inputs: electricity (recent history) (72%), calendar (time of day, weekday) (28%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.481 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 7.2%, NMBE -0.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2350 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
