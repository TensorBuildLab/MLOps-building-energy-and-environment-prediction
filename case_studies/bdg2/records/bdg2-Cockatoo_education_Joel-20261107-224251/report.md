# Run report: bdg2-Cockatoo_education_Joel

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -1.7 for 14 h (2017-01-28 16:00:00 to 2017-01-29 06:00:00); 57 such stretch(es), 16 d 11 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.6 for 8 h (2016-09-07 02:00:00 to 2016-09-07 10:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

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
| train | 2016-01-01 00:00:00 | 2017-06-09 23:00:00 | 11283 |
| val | 2017-06-11 00:00:00 | 2017-09-21 19:00:00 | 2393 |
| test | 2017-09-22 20:00:00 | 2017-12-31 23:00:00 | 2395 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 0.730 | 0.561 | 12.525 | -0.646 | 0.676 |
| gbm_change | ml | 0.781 | 0.610 | 13.388 | -3.834 | 0.630 |
| gbm | ml | 0.799 | 0.620 | 13.696 | -4.465 | 0.613 |
| persistence | baseline | 0.822 | 0.630 | 14.096 | -0.078 | 0.590 |
| same_time_yesterday | baseline | 0.822 | 0.630 | 14.096 | -0.078 | 0.590 |
| time_of_week_profile | baseline | 1.009 | 0.823 | 17.303 | -6.490 | 0.382 |
| time_of_day_profile | baseline | 1.012 | 0.827 | 17.360 | -6.492 | 0.378 |
| same_time_last_week | baseline | 1.128 | 0.863 | 19.340 | 1.698 | 0.228 |
| towt | baseline | 1.358 | 1.140 | 23.294 | -16.523 | -0.119 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.628 | 0.673 |
| MAE (kWh) | 0.456 | 0.473 |
| CV(RMSE) % | 11.024 | 11.822 |
| NMBE % | -0.768 | -0.156 |
| R² | 0.664 | 0.613 |

Skill vs persistence: **0.07** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.0% (limit 30%), NMBE -0.8% (limit ±10%): **passes**.

90% prediction interval: ±1.22 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-10 to 2017-08-19 | 1612 | 0.15 |
| 2017-08-19 to 2017-10-25 | 1612 | 0.05 |
| 2017-10-25 to 2017-12-31 | 1612 | 0.08 |

Pooled skill: **0.09**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 84% |
| calendar (time of day, weekday) | 6% |
| airTemperature | 6% |
| dewTemperature | 3% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
