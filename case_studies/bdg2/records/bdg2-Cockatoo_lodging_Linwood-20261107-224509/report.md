# Run report: bdg2-Cockatoo_lodging_Linwood

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
| ridge | ml | 3.452 | 2.580 | 23.305 | 0.094 | 0.545 |
| gbm_change | ml | 3.591 | 2.710 | 24.243 | -2.900 | 0.508 |
| gbm | ml | 3.600 | 2.723 | 24.305 | -3.985 | 0.505 |
| persistence | baseline | 3.978 | 2.899 | 26.861 | 0.030 | 0.396 |
| same_time_yesterday | baseline | 3.978 | 2.899 | 26.861 | 0.030 | 0.396 |
| towt | baseline | 5.135 | 4.204 | 34.673 | -10.741 | -0.007 |
| same_time_last_week | baseline | 5.205 | 3.947 | 35.142 | 4.012 | -0.034 |
| time_of_day_profile | baseline | 6.207 | 5.229 | 41.907 | -26.316 | -0.471 |
| time_of_week_profile | baseline | 6.209 | 5.222 | 41.920 | -26.319 | -0.472 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 3.693 | 4.334 |
| MAE (kWh) | 2.847 | 3.086 |
| CV(RMSE) % | 20.832 | 24.451 |
| NMBE % | -3.126 | -0.758 |
| R² | 0.586 | 0.429 |

Skill vs persistence: **0.15** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 20.8% (limit 30%), NMBE -3.1% (limit ±10%): **passes**.

90% prediction interval: ±5.56 kWh (width from validation errors); it contained 87% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-10 to 2017-08-19 | 1612 | 0.10 |
| 2017-08-19 to 2017-10-25 | 1612 | 0.19 |
| 2017-10-25 to 2017-12-31 | 1612 | 0.10 |

Pooled skill: **0.14**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 91% |
| calendar (time of day, weekday) | 6% |
| dewTemperature | 3% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
