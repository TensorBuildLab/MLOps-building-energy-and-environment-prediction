# Model card: bdg2-Bull_education_Miranda

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:40:05 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `e5dc9276663e9f00`, prepared `4254c18f132b7c93`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-11 18:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 2 to 552 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 19:00:00 to 2017-12-31 23:00:00.

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 23.042 | 25.215 |
| MAE (kWh) | 11.911 | 15.318 |
| CV(RMSE) % | 14.509 | 15.878 |
| NMBE % | -1.244 | -6.286 |
| R² | 0.322 | 0.188 |

Skill vs time_of_week_profile: 0.09.

90% prediction interval: ±21.4 kWh; it contained 88% of test values.

Main inputs: electricity (recent history) (61%), calendar (time of day, weekday) (39%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.086 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 14.5%, NMBE -1.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2559 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
