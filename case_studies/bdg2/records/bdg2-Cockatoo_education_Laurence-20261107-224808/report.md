# Run report: bdg2-Cockatoo_education_Laurence

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
| train | 2016-01-01 00:00:00 | 2017-06-09 22:00:00 | 11282 |
| val | 2017-06-10 23:00:00 | 2017-09-21 19:00:00 | 2393 |
| test | 2017-09-22 20:00:00 | 2017-12-31 23:00:00 | 2395 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 22.907 | 14.191 | 35.345 | 1.363 | 0.469 |
| gbm | ml | 23.650 | 14.758 | 36.492 | 2.318 | 0.435 |
| ridge | ml | 25.556 | 17.675 | 39.432 | 0.398 | 0.340 |
| towt | baseline | 27.380 | 19.708 | 42.247 | -2.214 | 0.242 |
| time_of_day_profile | baseline | 27.496 | 21.912 | 42.426 | -11.433 | 0.236 |
| time_of_week_profile | baseline | 27.776 | 21.628 | 42.858 | -11.381 | 0.220 |
| same_time_yesterday | baseline | 35.282 | 18.921 | 54.440 | -1.059 | -0.259 |
| persistence | baseline | 35.282 | 18.921 | 54.440 | -1.059 | -0.259 |
| same_time_last_week | baseline | 35.972 | 20.170 | 55.505 | -0.840 | -0.308 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 26.988 | 29.793 |
| MAE (kWh) | 18.745 | 20.749 |
| CV(RMSE) % | 35.970 | 39.708 |
| NMBE % | -0.438 | 2.079 |
| R² | 0.465 | 0.348 |

Skill vs towt: **0.09** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 36.0% (limit 30%), NMBE -0.4% (limit ±10%): **does not pass**.

90% prediction interval: ±39.5 kWh (width from validation errors); it contained 89% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-09 to 2017-08-19 | 1612 | 0.22 |
| 2017-08-19 to 2017-10-25 | 1612 | 0.11 |
| 2017-10-25 to 2017-12-31 | 1612 | 0.08 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 50% |
| electricity (recent history) | 49% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
