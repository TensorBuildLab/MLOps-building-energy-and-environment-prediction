# Model card: bdg2-Cockatoo_education_Orlando

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:49:59 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `f70c87d0e1dd06dd`, prepared `4a8da72e7094f49b`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-21 19:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 162 to 383 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-22 20:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 21.915 | 29.437 |
| MAE (kWh) | 13.835 | 20.416 |
| CV(RMSE) % | 8.879 | 11.926 |
| NMBE % | 1.498 | 5.685 |
| R² | 0.808 | 0.653 |

Skill vs time_of_week_profile: 0.26.

90% prediction interval: ±31.8 kWh; it contained 87% of test values.

Main inputs: electricity (recent history) (81%), calendar (time of day, weekday) (17%), airTemperature (2%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.256 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 8.9%, NMBE 1.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2395 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
