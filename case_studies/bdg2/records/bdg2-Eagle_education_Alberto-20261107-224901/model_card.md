# Model card: bdg2-Eagle_education_Alberto

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** time_of_week_profile 
- **Trained:** 2026-11-07T22:49:01 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `29d4878996c005e3`, prepared `d5b70a1cb178182a`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-01 13:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 113 to 621 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-02 14:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 32.174 | 32.174 |
| MAE (kWh) | 25.546 | 25.546 |
| CV(RMSE) % | 6.677 | 6.677 |
| NMBE % | 4.536 | 4.536 |
| R² | 0.568 | 0.568 |

Skill vs time_of_week_profile: 0.00.

90% prediction interval: ±26.8 kWh; it contained 57% of test values.

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 6.7%, NMBE 4.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2427 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'time_of_week_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
