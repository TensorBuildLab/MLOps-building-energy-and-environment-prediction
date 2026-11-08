# Model card: bdg2-Wolf_office_Elisabeth

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** time_of_day_profile 
- **Trained:** 2026-10-29T02:46:24 with bemlops 0.2.0.dev0 (code 8d12bd9)
- **Data fingerprint:** raw `cc9e149c927f5282`, prepared `a5a2ecc170e8de8d`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 30.1 to 181 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 07:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 11.201 | 11.201 |
| MAE (kWh) | 8.740 | 8.740 |
| CV(RMSE) % | 8.600 | 8.600 |
| NMBE % | -4.586 | -4.586 |
| R² | -0.084 | -0.084 |

Skill vs time_of_day_profile: 0.00.

90% prediction interval: ±13.1 kWh; it contained 80% of test values.

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | CV(RMSE) 8.6%, NMBE -4.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2608 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
