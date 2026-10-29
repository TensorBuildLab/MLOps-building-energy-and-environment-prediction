# Run report: bdg2-Peacock_education_Anita

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 17 h (2016-01-08 15:00:00 to 2016-01-09 08:00:00); 48 such stretch(es), 14 d 14 h in total. | prepare() treats these stretches as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 48 stuck stretch(es) set to missing. (110)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (58)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (11)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (65)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-27 02:00:00 | 12252 |
| val | 2017-05-28 03:00:00 | 2017-09-13 11:00:00 | 2601 |
| test | 2017-09-14 12:00:00 | 2017-12-31 23:00:00 | 2603 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 2.426 | 1.797 | 25.724 | -4.846 | 0.681 |
| gbm_change | ml | 2.433 | 1.629 | 25.795 | -5.478 | 0.679 |
| gbm | ml | 2.539 | 1.828 | 26.916 | -8.888 | 0.651 |
| persistence | baseline | 3.594 | 2.143 | 38.103 | 0.586 | 0.301 |
| same_time_yesterday | baseline | 3.594 | 2.143 | 38.103 | 0.586 | 0.301 |
| time_of_day_profile | baseline | 3.786 | 3.384 | 40.142 | -32.473 | 0.224 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 2.238 | 3.364 |
| MAE (kWh) | 1.727 | 2.154 |
| CV(RMSE) % | 23.804 | 35.780 |
| NMBE % | -9.062 | -0.039 |
| R² | 0.633 | 0.171 |

Skill vs persistence: **0.33** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 23.8% (limit 30%), NMBE -9.1% (limit ±10%): **passes**.

90% prediction interval: ±3.68 kWh (width from validation errors); it contained 93% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-08 | 1751 | 0.33 |
| 2017-08-08 to 2017-10-20 | 1751 | 0.40 |
| 2017-10-20 to 2017-12-31 | 1750 | 0.28 |

Pooled skill: **0.34**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 70% |
| calendar (time of day, weekday) | 30% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
