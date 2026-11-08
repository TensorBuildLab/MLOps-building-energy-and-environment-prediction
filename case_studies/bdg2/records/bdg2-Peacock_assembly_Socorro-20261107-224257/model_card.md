# Model card: bdg2-Peacock_assembly_Socorro

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(1.96282248134428)}
- **Trained:** 2026-11-07T22:42:57 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `6420f9d600cdfaa5`, prepared `b04e5bda9534902a`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1.14 to 94 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 7.857 | 12.158 |
| MAE (kWh) | 5.513 | 8.581 |
| CV(RMSE) % | 21.128 | 32.694 |
| NMBE % | 0.313 | -0.675 |
| R² | 0.692 | 0.262 |

Skill vs same_time_last_week: 0.35.

90% prediction interval: ±21.8 kWh; it contained 98% of test values.

Main inputs: electricity (recent history) (95%), calendar (time of day, weekday) (4%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.354 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 21.1%, NMBE 0.3% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2607 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
