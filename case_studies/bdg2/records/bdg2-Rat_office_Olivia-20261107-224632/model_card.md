# Model card: bdg2-Rat_office_Olivia

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:46:32 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `a3909d00eef2a395`, prepared `756f5dcdd7a7d89a`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 13:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 14.2 to 151 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 14:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 11.040 | 12.334 |
| MAE (kWh) | 7.855 | 8.233 |
| CV(RMSE) % | 18.895 | 21.110 |
| NMBE % | 2.380 | -0.904 |
| R² | 0.769 | 0.711 |

Skill vs same_time_last_week: 0.10.

90% prediction interval: ±17.7 kWh; it contained 92% of test values.

Main inputs: electricity (recent history) (82%), calendar (time of day, weekday) (16%), dewTemperature (2%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.105 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 18.9%, NMBE 2.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2601 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
