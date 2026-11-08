# Model card: bdg2-Crow_education_Omer

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:40:19 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `77da352fc38e0eb3`, prepared `ecf52b0138cbba77`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-07-31 01:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 159 to 918 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-08-01 02:00:00 to 2017-11-09 21:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 39.532 | 50.484 |
| MAE (kWh) | 27.758 | 33.468 |
| CV(RMSE) % | 11.663 | 14.894 |
| NMBE % | 0.182 | 1.362 |
| R² | 0.893 | 0.825 |

Skill vs same_time_last_week: 0.22.

90% prediction interval: ±55.9 kWh; it contained 88% of test values.

Main inputs: electricity (recent history) (77%), calendar (time of day, weekday) (23%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.217 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 11.7%, NMBE 0.2% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2419 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
