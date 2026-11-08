# Model card: bdg2-Gator_public_Latasha

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** time_of_day_profile 
- **Trained:** 2026-11-07T22:42:39 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `06ac3c1e21493010`, prepared `3f28cdd8acf331b8`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-08-15 00:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1.67 to 41.7 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-08-16 01:00:00 to 2017-12-30 05:00:00.

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 5.496 | 5.496 |
| MAE (kWh) | 4.314 | 4.314 |
| CV(RMSE) % | 32.854 | 32.854 |
| NMBE % | -11.805 | -11.805 |
| R² | 0.195 | 0.195 |

Skill vs time_of_day_profile: 0.00.

90% prediction interval: ±5.7 kWh; it contained 74% of test values.

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 32.9%, NMBE -11.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 521 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
