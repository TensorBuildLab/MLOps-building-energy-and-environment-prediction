# Run report: bdg2-Cockatoo_education_Claudine

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
| train | 2016-01-01 00:00:00 | 2017-06-09 23:00:00 | 11280 |
| val | 2017-06-11 00:00:00 | 2017-09-21 19:00:00 | 2393 |
| test | 2017-09-22 20:00:00 | 2017-12-31 23:00:00 | 2394 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 2.202 | 1.488 | 6.367 | -0.638 | 0.725 |
| gbm | ml | 2.360 | 1.598 | 6.826 | -1.006 | 0.684 |
| ridge | ml | 2.467 | 1.704 | 7.133 | 0.136 | 0.655 |
| same_time_last_week | baseline | 2.947 | 1.942 | 8.521 | 0.345 | 0.508 |
| same_time_yesterday | baseline | 3.316 | 2.120 | 9.591 | 0.013 | 0.377 |
| persistence | baseline | 3.316 | 2.120 | 9.591 | 0.013 | 0.377 |
| towt | baseline | 3.335 | 2.505 | 9.643 | -4.338 | 0.370 |
| time_of_day_profile | baseline | 5.564 | 4.950 | 16.091 | -13.839 | -0.754 |
| time_of_week_profile | baseline | 5.574 | 4.943 | 16.120 | -13.855 | -0.760 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 2.816 | 3.903 |
| MAE (kWh) | 1.971 | 2.768 |
| CV(RMSE) % | 7.034 | 9.751 |
| NMBE % | -0.357 | 0.546 |
| R² | 0.634 | 0.297 |

Skill vs same_time_last_week: **0.28** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 7.0% (limit 30%), NMBE -0.4% (limit ±10%): **passes**.

90% prediction interval: ±3.29 kWh (width from validation errors); it contained 82% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-10 to 2017-08-19 | 1612 | 0.28 |
| 2017-08-19 to 2017-10-25 | 1612 | 0.21 |
| 2017-10-25 to 2017-12-31 | 1611 | 0.30 |

Pooled skill: **0.26**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 66% |
| calendar (time of day, weekday) | 32% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
