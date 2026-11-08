# Model card: bdg2-Lamb_assembly_Delilah

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** persistence 
- **Trained:** 2026-11-07T22:43:51 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `789fe1390a247a9b`, prepared `4da0228edbfa06a5`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-14 02:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.0002 to 48.8 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-15 03:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.000 | 0.000 |
| MAE (kWh) | 0.000 | 0.000 |
| CV(RMSE) % | 0.000 | 0.000 |
| NMBE % | 0.000 | 0.000 |
| R² | 1.000 | 1.000 |

Skill vs persistence: nan.

90% prediction interval: ±0 kWh; it contained 100% of test values.

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | no skill recorded |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 0.0%, NMBE 0.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2589 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
