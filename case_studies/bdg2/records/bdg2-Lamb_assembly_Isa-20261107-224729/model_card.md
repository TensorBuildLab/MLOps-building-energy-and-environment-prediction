# Model card: bdg2-Lamb_assembly_Isa

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 50, 'max_leaf_nodes': 7, 'max_iter': 100, 'learning_rate': 0.2, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:47:29 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `f79a6375f9eb0483`, prepared `260b1e5b6bc4fd5d`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 20:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.0001 to 11.2 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 21:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.150 | 0.000 |
| MAE (kWh) | 0.082 | 0.000 |
| CV(RMSE) % | 150379.102 | 0.000 |
| NMBE % | -49777.901 | 0.000 |
| R² | -123074197210482408683463799426091319296.000 | 1.000 |

Skill vs persistence: nan.

90% prediction interval: ±1.04 kWh; it contained 100% of test values.

Main inputs: calendar (time of day, weekday) (60%), dewTemperature (23%), airTemperature (12%), windSpeed (4%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | no skill recorded |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 150379.1%, NMBE -49777.9% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2595 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
