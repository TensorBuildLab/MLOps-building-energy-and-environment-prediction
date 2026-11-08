# Model card: bdg2-Peacock_lodging_Wes

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:50:01 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `0f59fbd818457191`, prepared `031ae157e4bb0b8d`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 08:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 88.2 to 275 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 09:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 11.423 | 11.780 |
| MAE (kWh) | 8.652 | 8.723 |
| CV(RMSE) % | 7.886 | 8.133 |
| NMBE % | -1.110 | -0.082 |
| R² | 0.816 | 0.805 |

Skill vs persistence: 0.03.

90% prediction interval: ±18.8 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (94%), calendar (time of day, weekday) (6%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | no | skill 0.030 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 7.9%, NMBE -1.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2607 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.
- The model is barely better than persistence on test data (skill 0.03).

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
