# Run report: bdg2-Eagle_assembly_Margret

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 371.312 for 3 d 5 h (2016-07-16 05:00:00 to 2016-07-19 10:00:00); 4 such stretch(es), 5 d 17 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 4 stuck stretch(es) set to missing. (117)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-02 00:00:00 | 11900 |
| val | 2017-06-03 01:00:00 | 2017-09-16 14:00:00 | 2526 |
| test | 2017-09-17 15:00:00 | 2017-12-31 23:00:00 | 2527 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 39.276 | 28.618 | 13.216 | -1.727 | 0.844 |
| persistence | baseline | 41.265 | 25.385 | 13.885 | -0.374 | 0.827 |
| same_time_yesterday | baseline | 41.265 | 25.385 | 13.885 | -0.374 | 0.827 |
| gbm_change | ml | 43.785 | 31.830 | 14.733 | -6.345 | 0.806 |
| same_time_last_week | baseline | 61.603 | 42.405 | 20.728 | -1.891 | 0.615 |
| gbm | ml | 79.995 | 59.551 | 26.917 | -17.755 | 0.351 |
| time_of_day_profile | baseline | 153.477 | 126.541 | 51.642 | -42.145 | -1.389 |
| time_of_week_profile | baseline | 153.492 | 126.557 | 51.647 | -42.156 | -1.390 |
| towt | baseline | 161.384 | 134.830 | 54.303 | -45.129 | -1.642 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 33.479 | 41.832 |
| MAE (kWh) | 25.517 | 28.891 |
| CV(RMSE) % | 9.937 | 12.417 |
| NMBE % | -0.606 | -0.051 |
| R² | 0.754 | 0.616 |

Skill vs persistence: **0.20** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 9.9% (limit 30%), NMBE -0.6% (limit ±10%): **passes**.

90% prediction interval: ±66 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-02 to 2017-08-12 | 1701 | 0.12 |
| 2017-08-12 to 2017-10-22 | 1700 | 0.04 |
| 2017-10-22 to 2017-12-31 | 1700 | 0.19 |

Pooled skill: **0.11**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 92% |
| calendar (time of day, weekday) | 7% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
