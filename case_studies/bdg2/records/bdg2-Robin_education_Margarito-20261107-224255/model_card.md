# Model card: bdg2-Robin_education_Margarito

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** towt 
- **Trained:** 2026-11-07T22:42:55 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `9ba549b2b33ec498`, prepared `d7c48d79a8e869a9`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-23 23:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 219 to 948 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-25 00:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 49.840 | 49.840 |
| MAE (kWh) | 41.029 | 41.029 |
| CV(RMSE) % | 10.325 | 10.325 |
| NMBE % | -7.306 | -7.306 |
| R² | 0.386 | 0.386 |

Skill vs towt: 0.00.

90% prediction interval: ±59 kWh; it contained 82% of test values.

Main inputs: airTemperature (100%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 10.3%, NMBE -7.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2352 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'towt' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
