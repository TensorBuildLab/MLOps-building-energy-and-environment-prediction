# Model card: bdg2-Cockatoo_assembly_Ed

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:42:24 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `ea69cfbbdb221971`, prepared `70180266bebfcf83`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-22 00:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 62.1 to 417 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-23 01:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 19.075 | 20.661 |
| MAE (kWh) | 14.261 | 14.596 |
| CV(RMSE) % | 14.526 | 15.734 |
| NMBE % | -2.976 | -0.627 |
| R² | 0.774 | 0.735 |

Skill vs persistence: 0.08.

90% prediction interval: ±34.4 kWh; it contained 93% of test values.

Main inputs: electricity (recent history) (84%), airTemperature (7%), dewTemperature (6%), calendar (time of day, weekday) (3%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.077 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 14.5%, NMBE -3.0% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2390 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
