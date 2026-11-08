# Model card: bdg2-Eagle_assembly_Margret

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:47:12 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `50382ecb25f5982f`, prepared `7d5e18f9bc06a987`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-16 14:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 89.9 to 571 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-17 15:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 33.479 | 41.832 |
| MAE (kWh) | 25.517 | 28.891 |
| CV(RMSE) % | 9.937 | 12.417 |
| NMBE % | -0.606 | -0.051 |
| R² | 0.754 | 0.616 |

Skill vs persistence: 0.20.

90% prediction interval: ±66 kWh; it contained 94% of test values.

Main inputs: electricity (recent history) (92%), calendar (time of day, weekday) (7%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.200 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 9.9%, NMBE -0.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2527 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
