# Model card: bdg2-Bull_services_Nadine

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:50:17 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `2de6bbced2d6df01`, prepared `88cd4a9dd0127fb5`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 01:00:00 to 2017-09-11 15:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 8 to 577 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-12 16:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 7.381 | 8.722 |
| MAE (kWh) | 4.123 | 3.670 |
| CV(RMSE) % | 6.576 | 7.771 |
| NMBE % | -0.084 | -0.200 |
| R² | 0.652 | 0.515 |

Skill vs persistence: 0.15.

90% prediction interval: ±6.37 kWh; it contained 83% of test values.

Main inputs: electricity (recent history) (68%), calendar (time of day, weekday) (32%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.154 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 6.6%, NMBE -0.1% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2562 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
