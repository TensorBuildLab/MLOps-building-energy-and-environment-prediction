# Model card: bdg2-Mouse_health_Modesto

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:40:07 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `25f628c04716f4b5`, prepared `e9b6377a09d0ffc3`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-07-23 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 93.5 to 1.27e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-07-24 09:00:00 to 2017-10-23 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 56.405 | 68.021 |
| MAE (kWh) | 41.955 | 45.794 |
| CV(RMSE) % | 14.445 | 17.420 |
| NMBE % | -0.554 | -0.338 |
| R² | 0.618 | 0.444 |

Skill vs persistence: 0.17.

90% prediction interval: ±143 kWh; it contained 97% of test values.

Main inputs: electricity (recent history) (83%), calendar (time of day, weekday) (15%), dewTemperature (2%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.171 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 14.4%, NMBE -0.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2199 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
