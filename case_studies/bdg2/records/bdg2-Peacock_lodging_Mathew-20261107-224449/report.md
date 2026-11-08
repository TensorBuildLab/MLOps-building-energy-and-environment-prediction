# Run report: bdg2-Peacock_lodging_Mathew

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 17 h (2016-01-08 15:00:00 to 2016-01-09 08:00:00); 48 such stretch(es), 14 d 14 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

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
| train | 2016-01-01 00:00:00 | 2017-05-27 06:00:00 | 12246 |
| val | 2017-05-28 07:00:00 | 2017-09-13 14:00:00 | 2600 |
| test | 2017-09-14 15:00:00 | 2017-12-31 23:00:00 | 2601 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 4.075 | 2.117 | 10.545 | 0.118 | 0.751 |
| same_time_yesterday | baseline | 4.075 | 2.117 | 10.545 | 0.118 | 0.751 |
| ridge | ml | 4.407 | 2.940 | 11.404 | -2.096 | 0.708 |
| gbm_change | ml | 4.421 | 3.380 | 11.441 | -5.004 | 0.706 |
| same_time_last_week | baseline | 8.850 | 5.504 | 22.899 | -0.888 | -0.176 |
| gbm | ml | 8.867 | 8.255 | 22.944 | -18.147 | -0.181 |
| towt | baseline | 17.840 | 16.537 | 46.163 | -40.722 | -3.780 |
| time_of_day_profile | baseline | 21.441 | 20.025 | 55.481 | -50.206 | -5.905 |
| time_of_week_profile | baseline | 21.445 | 20.006 | 55.492 | -50.178 | -5.908 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 7.269 | 7.269 |
| MAE (kWh) | 4.933 | 4.933 |
| CV(RMSE) % | 13.341 | 13.341 |
| NMBE % | -0.329 | -0.329 |
| R² | 0.506 | 0.506 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 13.3% (limit 30%), NMBE -0.3% (limit ±10%): **passes**.

90% prediction interval: ±5.95 kWh (width from validation errors); it contained 70% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-08 | 1750 | 0.00 |
| 2017-08-08 to 2017-10-20 | 1750 | 0.00 |
| 2017-10-20 to 2017-12-31 | 1749 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 100% |

> Warning: No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
