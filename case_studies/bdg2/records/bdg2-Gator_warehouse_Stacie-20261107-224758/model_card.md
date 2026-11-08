# Model card: bdg2-Gator_warehouse_Stacie

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** towt 
- **Trained:** 2026-11-07T22:47:58 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `af6e83911cbb0c9c`, prepared `0721b633c90d6c52`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-02 00:00:00 to 2017-09-08 02:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1.5 to 45 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-10 00:00:00 to 2017-12-31 05:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 4.889 | 4.889 |
| MAE (kWh) | 2.881 | 2.881 |
| CV(RMSE) % | 29.031 | 29.031 |
| NMBE % | -9.961 | -9.961 |
| R² | 0.549 | 0.549 |

Skill vs towt: 0.00.

90% prediction interval: ±6.3 kWh; it contained 90% of test values.

Main inputs: airTemperature (100%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.000 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 29.0%, NMBE -10.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 588 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- No machine-learning model beat the 'towt' baseline on validation data. Look for better inputs before deploying anything more complex.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
