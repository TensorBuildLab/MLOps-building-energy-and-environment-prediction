# Run report: bdg2-Cockatoo_assembly_Ed

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
| train | 2016-01-01 00:00:00 | 2017-06-10 09:00:00 | 11260 |
| val | 2017-06-11 10:00:00 | 2017-09-22 00:00:00 | 2388 |
| test | 2017-09-23 01:00:00 | 2017-12-31 23:00:00 | 2390 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 21.766 | 16.107 | 14.389 | -4.843 | 0.753 |
| persistence | baseline | 22.166 | 15.257 | 14.653 | 0.048 | 0.743 |
| same_time_yesterday | baseline | 22.166 | 15.257 | 14.653 | 0.048 | 0.743 |
| gbm_change | ml | 27.616 | 21.496 | 18.256 | -10.566 | 0.602 |
| gbm | ml | 29.678 | 23.833 | 19.619 | -12.930 | 0.540 |
| same_time_last_week | baseline | 33.801 | 22.256 | 22.344 | 1.904 | 0.404 |
| time_of_day_profile | baseline | 35.267 | 26.368 | 23.314 | -11.127 | 0.351 |
| time_of_week_profile | baseline | 35.364 | 26.515 | 23.377 | -11.147 | 0.347 |
| towt | baseline | 74.994 | 60.164 | 49.575 | -37.757 | -1.936 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 19.075 | 20.661 |
| MAE (kWh) | 14.261 | 14.596 |
| CV(RMSE) % | 14.526 | 15.734 |
| NMBE % | -2.976 | -0.627 |
| R² | 0.774 | 0.735 |

Skill vs persistence: **0.08** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.5% (limit 30%), NMBE -3.0% (limit ±10%): **passes**.

90% prediction interval: ±34.4 kWh (width from validation errors); it contained 93% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-10 to 2017-08-19 | 1609 | -0.04 |
| 2017-08-19 to 2017-10-25 | 1609 | 0.13 |
| 2017-10-26 to 2017-12-31 | 1608 | 0.07 |

Pooled skill: **0.05**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 84% |
| airTemperature | 7% |
| dewTemperature | 6% |
| calendar (time of day, weekday) | 3% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
