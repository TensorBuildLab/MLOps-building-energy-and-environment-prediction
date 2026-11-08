# Model card: bdg2-Bear_education_Rebecca

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:46:56 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `7cdddf4c9a0e0b9c`, prepared `82c2dd09510b115a`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-11 21:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 504 to 1.06e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 22:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 35.987 | 44.044 |
| MAE (kWh) | 26.977 | 31.062 |
| CV(RMSE) % | 4.791 | 5.863 |
| NMBE % | -1.134 | -0.059 |
| R² | 0.772 | 0.659 |

Skill vs persistence: 0.18.

90% prediction interval: ±54.7 kWh; it contained 89% of test values.

Main inputs: electricity (recent history) (76%), calendar (time of day, weekday) (19%), airTemperature (4%), windSpeed (1%), dewTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.183 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 4.8%, NMBE -1.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2601 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
