# Run report: bdg2-Eagle_public_Missy

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 19.2359 for 2 d 13 h (2016-07-16 05:00:00 to 2016-07-18 18:00:00); 5 such stretch(es), 4 d 15 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 5 stuck stretch(es) set to missing. (86)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-21 20:00:00 | 11888 |
| val | 2017-05-22 21:00:00 | 2017-09-06 01:00:00 | 2523 |
| test | 2017-09-07 02:00:00 | 2017-12-31 23:00:00 | 2525 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 6.128 | 4.238 | 18.541 | -0.172 | 0.672 |
| gbm | ml | 6.186 | 4.374 | 18.715 | 0.018 | 0.666 |
| ridge | ml | 6.379 | 4.496 | 19.299 | 1.129 | 0.645 |
| towt | baseline | 7.419 | 5.134 | 22.446 | 2.684 | 0.519 |
| time_of_week_profile | baseline | 7.687 | 5.224 | 23.258 | 4.916 | 0.484 |
| time_of_day_profile | baseline | 7.778 | 5.307 | 23.532 | 4.894 | 0.472 |
| same_time_yesterday | baseline | 7.837 | 4.736 | 23.710 | 0.304 | 0.464 |
| persistence | baseline | 7.837 | 4.736 | 23.710 | 0.304 | 0.464 |
| same_time_last_week | baseline | 8.354 | 5.183 | 25.276 | 0.786 | 0.390 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 5.918 | 7.095 |
| MAE (kWh) | 4.113 | 5.120 |
| CV(RMSE) % | 18.602 | 22.303 |
| NMBE % | 2.746 | 1.153 |
| R² | 0.657 | 0.508 |

Skill vs towt: **0.17** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 18.6% (limit 30%), NMBE 2.7% (limit ±10%): **passes**.

90% prediction interval: ±9.11 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-21 to 2017-08-01 | 1699 | 0.22 |
| 2017-08-01 to 2017-10-11 | 1699 | 0.07 |
| 2017-10-11 to 2017-12-31 | 1698 | 0.28 |

Pooled skill: **0.19**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 85% |
| calendar (time of day, weekday) | 15% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
