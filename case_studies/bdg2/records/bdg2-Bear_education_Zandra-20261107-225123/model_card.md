# Model card: bdg2-Bear_education_Zandra

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:51:23 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `2e46cd13a7353031`, prepared `822115df8fbe8923`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-12 10:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 209 to 1.28e+03 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-13 11:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 20.823 | 27.081 |
| MAE (kWh) | 16.674 | 17.497 |
| CV(RMSE) % | 2.256 | 2.934 |
| NMBE % | -0.712 | -0.094 |
| R² | 0.689 | 0.475 |

Skill vs persistence: 0.23.

90% prediction interval: ±53.2 kWh; it contained 99% of test values.

Main inputs: electricity (recent history) (54%), calendar (time of day, weekday) (46%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.231 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 2.3%, NMBE -0.7% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2592 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
