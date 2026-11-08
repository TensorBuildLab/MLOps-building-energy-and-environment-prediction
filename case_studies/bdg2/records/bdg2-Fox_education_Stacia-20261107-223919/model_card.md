# Model card: bdg2-Fox_education_Stacia

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** time_of_day_profile 
- **Trained:** 2026-11-07T22:39:19 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `02f211f5fd4044a6`, prepared `1ce676f2429475ab`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-16 02:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1.21 to 97.8 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-17 03:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 4.486 | 4.486 |
| MAE (kWh) | 3.359 | 3.359 |
| CV(RMSE) % | 5.666 | 5.666 |
| NMBE % | 3.469 | 3.469 |
| R² | 0.035 | 0.035 |

Skill vs time_of_day_profile: 0.00.

90% prediction interval: ±3.61 kWh; it contained 61% of test values.

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 5.7%, NMBE 3.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2541 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
