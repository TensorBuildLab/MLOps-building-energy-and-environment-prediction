# Model card: bdg2-Mouse_health_Justin

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:38:05 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `422843cef6359c51`, prepared `9374d25fb3f490be`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-07-23 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.0017 to 1.49e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-07-24 07:00:00 to 2017-10-23 23:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 80.760 | 100.523 |
| MAE (kWh) | 60.892 | 79.548 |
| CV(RMSE) % | 9.590 | 11.937 |
| NMBE % | -0.748 | 1.693 |
| R² | 0.809 | 0.704 |

Skill vs towt: 0.20.

90% prediction interval: ±159 kWh; it contained 96% of test values.

Main inputs: electricity (recent history) (67%), calendar (time of day, weekday) (26%), airTemperature (7%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.197 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 9.6%, NMBE -0.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2197 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
