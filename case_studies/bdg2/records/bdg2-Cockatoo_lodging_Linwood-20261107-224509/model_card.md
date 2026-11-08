# Model card: bdg2-Cockatoo_lodging_Linwood

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:45:09 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `45da21b650581842`, prepared `f6b9bd29789caa64`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-21 19:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 5.1 to 42.8 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-22 20:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 3.693 | 4.334 |
| MAE (kWh) | 2.847 | 3.086 |
| CV(RMSE) % | 20.832 | 24.451 |
| NMBE % | -3.126 | -0.758 |
| R² | 0.586 | 0.429 |

Skill vs persistence: 0.15.

90% prediction interval: ±5.56 kWh; it contained 87% of test values.

Main inputs: electricity (recent history) (91%), calendar (time of day, weekday) (6%), dewTemperature (3%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.148 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 20.8%, NMBE -3.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2395 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
