# Model card: bdg2-Eagle_public_Preston

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:46:06 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `dd98f674cb63a985`, prepared `639c34ce5345645a`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-14 19:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 82.4 to 574 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-15 20:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 36.073 | 51.693 |
| MAE (kWh) | 25.875 | 28.354 |
| CV(RMSE) % | 11.615 | 16.645 |
| NMBE % | -0.773 | -2.587 |
| R² | 0.760 | 0.507 |

Skill vs same_time_last_week: 0.30.

90% prediction interval: ±47.2 kWh; it contained 86% of test values.

Main inputs: electricity (recent history) (68%), calendar (time of day, weekday) (29%), airTemperature (3%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.302 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 11.6%, NMBE -0.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2569 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
