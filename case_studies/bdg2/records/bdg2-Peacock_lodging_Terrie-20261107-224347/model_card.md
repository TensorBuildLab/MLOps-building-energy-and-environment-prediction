# Model card: bdg2-Peacock_lodging_Terrie

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:43:47 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `c90b90137814bc56`, prepared `88697efc8d4118f2`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 13:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 10.7 to 80.2 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 14:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 6.349 | 7.869 |
| MAE (kWh) | 5.070 | 5.827 |
| CV(RMSE) % | 19.115 | 23.692 |
| NMBE % | -4.528 | -0.073 |
| R² | 0.236 | -0.175 |

Skill vs persistence: 0.19.

90% prediction interval: ±9.52 kWh; it contained 88% of test values.

Main inputs: electricity (recent history) (84%), calendar (time of day, weekday) (15%), dewTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.193 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 19.1%, NMBE -4.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2602 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
