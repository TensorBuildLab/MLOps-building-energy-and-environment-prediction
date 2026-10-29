# Run report: bdg2-Cockatoo_public_Caleb

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -1.7 for 14 h (2017-01-28 16:00:00 to 2017-01-29 06:00:00); 57 such stretch(es), 16 d 11 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.6 for 8 h (2016-09-07 02:00:00 to 2016-09-07 10:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 57 stuck stretch(es) set to missing. (108)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (323)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (273)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (306)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-09 17:00:00 | 11277 |
| val | 2017-06-10 18:00:00 | 2017-09-21 15:00:00 | 2392 |
| test | 2017-09-22 16:00:00 | 2017-12-31 23:00:00 | 2393 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 18.821 | 13.071 | 12.068 | -2.043 | 0.832 |
| gbm_change | ml | 19.222 | 14.038 | 12.325 | -4.489 | 0.824 |
| gbm | ml | 19.970 | 15.039 | 12.805 | -6.372 | 0.810 |
| persistence | baseline | 36.797 | 21.174 | 23.593 | -0.244 | 0.356 |
| same_time_yesterday | baseline | 36.797 | 21.174 | 23.593 | -0.244 | 0.356 |
| time_of_day_profile | baseline | 44.403 | 37.982 | 28.470 | -24.181 | 0.062 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 21.403 | 30.320 |
| MAE (kWh) | 14.334 | 18.426 |
| CV(RMSE) % | 14.106 | 19.983 |
| NMBE % | -4.127 | -0.598 |
| R² | 0.720 | 0.437 |

Skill vs persistence: **0.29** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.1% (limit 30%), NMBE -4.1% (limit ±10%): **passes**.

90% prediction interval: ±30.9 kWh (width from validation errors); it contained 88% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-09 to 2017-08-19 | 1611 | 0.51 |
| 2017-08-19 to 2017-10-25 | 1611 | 0.48 |
| 2017-10-25 to 2017-12-31 | 1611 | 0.18 |

Pooled skill: **0.41**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 82% |
| calendar (time of day, weekday) | 18% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
