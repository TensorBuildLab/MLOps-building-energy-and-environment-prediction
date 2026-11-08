# Model card: bdg2-Gator_office_Julie

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** gbm {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}
- **Trained:** 2026-11-07T22:48:05 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `311a992ff3193976`, prepared `d87c61eeb787aba1`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-09 02:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.333 to 15.3 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-10 03:00:00 to 2017-12-30 05:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 2.179 | 2.442 |
| MAE (kWh) | 1.573 | 1.786 |
| CV(RMSE) % | 30.861 | 34.572 |
| NMBE % | -6.377 | 1.959 |
| R² | 0.653 | 0.564 |

Skill vs towt: 0.11.

90% prediction interval: ±4.62 kWh; it contained 95% of test values.

Main inputs: calendar (time of day, weekday) (69%), dewTemperature (17%), electricity (recent history) (13%), windSpeed (1%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.107 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 30.9%, NMBE -6.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 585 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
