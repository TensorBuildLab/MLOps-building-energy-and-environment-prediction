# Model card: bdg2-Peacock_education_Forest

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:38:38 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `c64d7905950cb027`, prepared `26d31e493687c6fc`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 12:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 35.1 to 162 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 13:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 9.502 | 10.645 |
| MAE (kWh) | 6.819 | 7.190 |
| CV(RMSE) % | 10.428 | 11.682 |
| NMBE % | 0.923 | 0.120 |
| R² | 0.662 | 0.576 |

Skill vs persistence: 0.11.

90% prediction interval: ±11.7 kWh; it contained 84% of test values.

Main inputs: electricity (recent history) (86%), calendar (time of day, weekday) (13%), dewTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.107 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 10.4%, NMBE 0.9% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2603 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
