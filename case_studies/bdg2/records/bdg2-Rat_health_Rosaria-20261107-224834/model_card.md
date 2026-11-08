# Model card: bdg2-Rat_health_Rosaria

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm_change {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}
- **Trained:** 2026-11-07T22:48:34 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `4ad2d6a78f398504`, prepared `25fc374a7176e714`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 14:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 5.74 to 84.2 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 15:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 5.698 | 9.223 |
| MAE (kWh) | 4.023 | 7.277 |
| CV(RMSE) % | 17.800 | 28.810 |
| NMBE % | 3.540 | 6.215 |
| R² | 0.854 | 0.618 |

Skill vs towt: 0.38.

90% prediction interval: ±11.1 kWh; it contained 94% of test values.

Main inputs: electricity (recent history) (77%), calendar (time of day, weekday) (21%), airTemperature (1%), dewTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.382 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 17.8%, NMBE 3.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2600 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
