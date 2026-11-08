# Model card: bdg2-Eagle_lodging_Edgardo

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:45:21 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `6b973cde7dbf65d9`, prepared `5db991aa4db292cd`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-14 22:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 14.8 to 103 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-15 23:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 8.242 | 9.131 |
| MAE (kWh) | 5.901 | 6.256 |
| CV(RMSE) % | 15.251 | 16.896 |
| NMBE % | -0.623 | -0.364 |
| R² | 0.772 | 0.721 |

Skill vs persistence: 0.10.

90% prediction interval: ±9.72 kWh; it contained 82% of test values.

Main inputs: electricity (recent history) (97%), calendar (time of day, weekday) (2%), airTemperature (1%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.097 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 15.3%, NMBE -0.6% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2567 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
