# Model card: bdg2-Rat_assembly_Pauline

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:41:21 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `4d961c8cc7754dac`, prepared `1f41ddb0a7665f2b`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-11 19:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.24 to 9.84 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 20:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.538 | 0.598 |
| MAE (kWh) | 0.287 | 0.246 |
| CV(RMSE) % | 61.091 | 67.870 |
| NMBE % | -13.539 | -5.587 |
| R² | 0.330 | 0.173 |

Skill vs persistence: 0.10.

90% prediction interval: ±1.6 kWh; it contained 97% of test values.

Main inputs: electricity (recent history) (96%), dewTemperature (3%), calendar (time of day, weekday) (1%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.100 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 61.1%, NMBE -13.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2520 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
