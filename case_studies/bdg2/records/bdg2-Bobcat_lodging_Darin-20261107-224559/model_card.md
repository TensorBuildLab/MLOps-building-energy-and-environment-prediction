# Model card: bdg2-Bobcat_lodging_Darin

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:45:59 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `1957bf1ca848f0d5`, prepared `8d9d55249ac30c46`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-19 18:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.5 to 299 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-20 19:00:00 to 2017-12-31 23:00:00.

| Metric | Model | same_time_yesterday |
|---|---|---|
| RMSE (kWh) | 17.577 | 20.558 |
| MAE (kWh) | 11.017 | 12.275 |
| CV(RMSE) % | 13.831 | 16.177 |
| NMBE % | -1.389 | -0.156 |
| R² | 0.554 | 0.390 |

Skill vs same_time_yesterday: 0.15.

90% prediction interval: ±23.5 kWh; it contained 91% of test values.

Main inputs: electricity (recent history) (89%), calendar (time of day, weekday) (8%), airTemperature (3%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.145 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 13.8%, NMBE -1.4% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2450 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
