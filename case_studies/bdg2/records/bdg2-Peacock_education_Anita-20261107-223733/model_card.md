# Model card: bdg2-Peacock_education_Anita

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:37:33 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `738901d93e6ba117`, prepared `b2eece601bb6b809`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 11:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 1.55 to 32.8 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 12:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 2.238 | 2.425 |
| MAE (kWh) | 1.727 | 1.618 |
| CV(RMSE) % | 23.804 | 25.793 |
| NMBE % | -9.062 | 0.439 |
| R² | 0.633 | 0.569 |

Skill vs same_time_last_week: 0.08.

90% prediction interval: ±3.68 kWh; it contained 93% of test values.

Main inputs: electricity (recent history) (70%), calendar (time of day, weekday) (30%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.077 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 23.8%, NMBE -9.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2603 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
