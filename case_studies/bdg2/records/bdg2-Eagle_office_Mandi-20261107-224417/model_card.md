# Model card: bdg2-Eagle_office_Mandi

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** towt 
- **Trained:** 2026-11-07T22:44:17 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `c86da80f6d3b618f`, prepared `b3dc4b2873fdf8ed`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-01 19:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 6.24 to 22.8 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-02 20:00:00 to 2017-12-31 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 1.048 | 1.048 |
| MAE (kWh) | 0.849 | 0.849 |
| CV(RMSE) % | 5.888 | 5.888 |
| NMBE % | 4.077 | 4.077 |
| R² | 0.671 | 0.671 |

Skill vs towt: 0.00.

90% prediction interval: ±0.895 kWh; it contained 58% of test values.

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 5.9%, NMBE 4.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2421 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'towt' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
