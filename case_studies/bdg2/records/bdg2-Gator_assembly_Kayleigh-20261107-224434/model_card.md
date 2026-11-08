# Model card: bdg2-Gator_assembly_Kayleigh

## Model

- **Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)
- **Model:** ridge {'model__alpha': np.float64(19.549524484259873)}
- **Trained:** 2026-11-07T22:44:34 with bemlops 0.3.1 (code a89b059)
- **Data fingerprint:** raw `873cfe1b7341405d`, prepared `23d4496104fa5396`

## Intended use

Day-ahead hourly electricity forecast for operations planning.

Valid only for this building and these inputs, at this time step and horizon.

## Training data

- **Period:** 2016-01-01 00:00:00 to 2017-08-25 14:00:00 (train + validation)
- **Inputs:** `airTemperature` (outdoor_air_temperature, degC), `dewTemperature` (other), `windSpeed` (wind_speed, m/s)
- **Target range seen:** 0.167 to 32 kWh

## Performance (held-out test period, time-ordered)

Test period 2017-08-27 00:00:00 to 2017-12-31 05:00:00.

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 8.789 | 10.112 |
| MAE (kWh) | 6.727 | 7.696 |
| CV(RMSE) % | 74.904 | 86.182 |
| NMBE % | 25.783 | 46.248 |
| R² | 0.310 | 0.086 |

Skill vs towt: 0.13.

90% prediction interval: ±5.32 kWh; it contained 46% of test values.

Main inputs: electricity (recent history) (85%), calendar (time of day, weekday) (15%).

ASHRAE Guideline 14 (hourly): does not pass.

## Promotion gates

| Gate | Passed | Detail |
|---|---|---|
| data_check_resolved | yes | all errors fixed or accepted with reasons |
| beats_baseline | yes | skill 0.131 vs required 0.05 |
| guideline14 | yes | reported, not gated (forecast): CV(RMSE) 74.9%, NMBE 25.8% |
| no_suspicious_inputs | yes | none |
| enough_test_data | yes | 510 test rows (need 200) |

## Limitations

- Inputs outside the training range, sensor faults and operation changes (schedules, setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.

## Monitoring

Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; promote the new model only if it passes the gates and beats this one on the same recent data.
