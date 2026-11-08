# Run report: bdg2-Cockatoo_assembly_Pierre

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
| train | 2016-01-01 00:00:00 | 2017-06-10 00:00:00 | 11280 |
| val | 2017-06-11 01:00:00 | 2017-09-21 20:00:00 | 2393 |
| test | 2017-09-22 21:00:00 | 2017-12-31 23:00:00 | 2394 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 2.168 | 1.626 | 13.064 | 4.250 | 0.737 |
| gbm_change | ml | 2.390 | 1.838 | 14.401 | 7.409 | 0.681 |
| gbm | ml | 2.420 | 1.882 | 14.579 | 8.299 | 0.673 |
| persistence | baseline | 2.552 | 1.908 | 15.377 | 0.433 | 0.636 |
| same_time_yesterday | baseline | 2.552 | 1.908 | 15.377 | 0.433 | 0.636 |
| same_time_last_week | baseline | 2.600 | 2.020 | 15.666 | 1.524 | 0.622 |
| time_of_week_profile | baseline | 3.102 | 2.381 | 18.692 | 11.121 | 0.462 |
| time_of_day_profile | baseline | 3.151 | 2.389 | 18.983 | 11.121 | 0.446 |
| towt | baseline | 3.701 | 2.970 | 22.296 | 16.505 | 0.235 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 1.932 | 2.311 |
| MAE (kWh) | 1.447 | 1.683 |
| CV(RMSE) % | 11.805 | 14.119 |
| NMBE % | -0.736 | -0.328 |
| R² | 0.713 | 0.590 |

Skill vs persistence: **0.16** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.8% (limit 30%), NMBE -0.7% (limit ±10%): **passes**.

90% prediction interval: ±3.66 kWh (width from validation errors); it contained 93% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-10 to 2017-08-19 | 1612 | 0.12 |
| 2017-08-19 to 2017-10-25 | 1612 | 0.19 |
| 2017-10-25 to 2017-12-31 | 1611 | 0.18 |

Pooled skill: **0.16**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 84% |
| calendar (time of day, weekday) | 14% |
| dewTemperature | 2% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
