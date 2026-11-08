# Run report: bdg2-Cockatoo_assembly_Valencia

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
| train | 2016-01-01 00:00:00 | 2017-06-09 23:00:00 | 11281 |
| val | 2017-06-11 00:00:00 | 2017-09-21 19:00:00 | 2393 |
| test | 2017-09-22 20:00:00 | 2017-12-31 23:00:00 | 2395 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 15.711 | 7.381 | 23.884 | 0.644 | 0.736 |
| same_time_yesterday | baseline | 15.711 | 7.381 | 23.884 | 0.644 | 0.736 |
| ridge | ml | 16.109 | 9.878 | 24.488 | -7.238 | 0.722 |
| gbm_change | ml | 22.819 | 16.000 | 34.689 | -18.322 | 0.442 |
| same_time_last_week | baseline | 24.981 | 11.782 | 37.977 | 6.899 | 0.332 |
| gbm | ml | 42.279 | 36.222 | 64.273 | -50.150 | -0.914 |
| time_of_day_profile | baseline | 55.346 | 52.714 | 84.137 | -70.206 | -2.280 |
| time_of_week_profile | baseline | 55.361 | 52.687 | 84.159 | -70.227 | -2.282 |
| towt | baseline | 64.936 | 59.378 | 98.717 | -79.974 | -3.515 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 33.489 | 33.489 |
| MAE (kWh) | 23.355 | 23.355 |
| CV(RMSE) % | 23.486 | 23.486 |
| NMBE % | -0.160 | -0.160 |
| R² | 0.168 | 0.168 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 23.5% (limit 30%), NMBE -0.2% (limit ±10%): **passes**.

90% prediction interval: ±14.3 kWh (width from validation errors); it contained 49% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-10 to 2017-08-19 | 1612 | 0.00 |
| 2017-08-19 to 2017-10-25 | 1612 | 0.00 |
| 2017-10-25 to 2017-12-31 | 1612 | 0.00 |

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
