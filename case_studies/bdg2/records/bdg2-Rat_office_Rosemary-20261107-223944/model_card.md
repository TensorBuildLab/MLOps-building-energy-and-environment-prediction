# Model card: bdg2-Rat_office_Rosemary

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** towt 
- **Trained:** 2026-11-07T22:39:44 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `f7f85761e9eb5747`, prepared `bacda88abdaf4cd6`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 13:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 3.97 to 42.2 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 14:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 3.647 | 3.647 |
| MAE (kWh) | 2.819 | 2.819 |
| CV(RMSE) % | 21.968 | 21.968 |
| NMBE % | 4.720 | 4.720 |
| R² | 0.463 | 0.463 |

Skill vs towt: 0.00.

90% prediction interval: ±6.73 kWh; it contained 94% of test values.

Main inputs: airTemperature (100%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 22.0%, NMBE 4.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2601 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'towt' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
