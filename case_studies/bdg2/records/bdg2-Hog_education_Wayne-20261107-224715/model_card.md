# Model card: bdg2-Hog_education_Wayne

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** time_of_week_profile 
- **Trained:** 2026-11-07T22:47:15 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `3914f9b9d47c746c`, prepared `f353313981cc0435`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1.76 to 341 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 23.310 | 23.310 |
| MAE (kWh) | 20.061 | 20.061 |
| CV(RMSE) % | 15.430 | 15.430 |
| NMBE % | -10.670 | -10.670 |
| R² | 0.554 | 0.554 |

Skill vs time_of_week_profile: 0.00.

90% prediction interval: ±26.8 kWh; it contained 80% of test values.

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 15.4%, NMBE -10.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2607 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'time_of_week_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
