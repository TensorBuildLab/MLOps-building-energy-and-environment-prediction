# Model card: bdg2-Wolf_science_Alfreda

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:42:07 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `28ed04ae8127f5a9`, prepared `beb006fe55fcd225`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-09-13 06:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 35.8 to 124 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-09-14 07:00:00 to 2017-12-31 23:00:00.

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 8.159 | 9.241 |
| MAE (kWh) | 5.853 | 5.706 |
| CV(RMSE) % | 10.545 | 11.944 |
| NMBE % | -2.475 | -0.034 |
| R² | 0.438 | 0.279 |

Skill vs persistence: 0.12.

90% prediction interval: ±13.9 kWh; it contained 92% of test values.

Main inputs: electricity (recent history) (72%), calendar (time of day, weekday) (28%).

ASHRAE Guideline 14 (hourly): passes.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.117 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 10.5%, NMBE -2.5% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 2608 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
