# Model card: bdg2-Bear_education_Derek

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:45:06 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `268dc2cf3dd65c46`, prepared `ffdde787c59748b6`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 09:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.016 to 269 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 10:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 22.674 | 24.051 |
| MAE (kWh) | 10.512 | 11.336 |
| CV(RMSE) % | 12.427 | 13.181 |
| NMBE % | -0.990 | -0.375 |
| R² | 0.639 | 0.594 |

Skill vs persistence: 0.06.

90% prediction interval: ±16 kWh; it contained 89% of test values.

Main inputs: electricity (recent history) (95%), calendar (time of day, weekday) (5%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.057 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 12.4%, NMBE -1.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2598 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
