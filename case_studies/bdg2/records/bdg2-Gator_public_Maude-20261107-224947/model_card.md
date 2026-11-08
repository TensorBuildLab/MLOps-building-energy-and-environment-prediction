# Model card: bdg2-Gator_public_Maude

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** towt 
- **Trained:** 2026-11-07T22:49:47 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `cba78414f430c607`, prepared `6934196935b4b856`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-17 00:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1.21 to 212 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-18 01:00:00 to 2017-12-31 05:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 25.874 | 25.874 |
| MAE (kWh) | 16.106 | 16.106 |
| CV(RMSE) % | 28.709 | 28.709 |
| NMBE % | 1.207 | 1.207 |
| R² | 0.521 | 0.521 |

Skill vs towt: 0.00.

90% prediction interval: ±18 kWh; it contained 78% of test values.

Main inputs: airTemperature (100%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 28.7%, NMBE 1.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 527 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'towt' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
