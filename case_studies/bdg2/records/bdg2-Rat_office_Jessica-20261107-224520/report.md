# Run report: bdg2-Rat_office_Jessica

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 18.3 for 11 h (2016-10-01 20:00:00 to 2016-10-02 07:00:00); 51 such stretch(es), 15 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2016-08-07 22:00:00 to 2016-08-08 04:00:00); 2 such stretch(es), 12 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 51 stuck stretch(es) set to missing. (107)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (60)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (12)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (16)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-21 04:00:00 | 12118 |
| val | 2017-05-22 05:00:00 | 2017-09-13 08:00:00 | 2572 |
| test | 2017-09-14 09:00:00 | 2017-12-31 23:00:00 | 2574 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 42.642 | 31.222 | 6.358 | -1.883 | 0.882 |
| gbm | ml | 43.966 | 31.605 | 6.555 | -1.916 | 0.874 |
| ridge | ml | 50.753 | 38.657 | 7.567 | -2.118 | 0.832 |
| same_time_last_week | baseline | 54.630 | 38.644 | 8.145 | -1.101 | 0.806 |
| time_of_week_profile | baseline | 70.620 | 54.775 | 10.529 | -7.024 | 0.675 |
| time_of_day_profile | baseline | 73.797 | 57.128 | 11.003 | -7.023 | 0.646 |
| towt | baseline | 91.363 | 78.014 | 13.622 | -11.341 | 0.457 |
| persistence | baseline | 94.024 | 57.938 | 14.019 | -0.161 | 0.425 |
| same_time_yesterday | baseline | 94.024 | 57.938 | 14.019 | -0.161 | 0.425 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 69.964 | 92.041 |
| MAE (kWh) | 47.212 | 62.243 |
| CV(RMSE) % | 10.664 | 14.029 |
| NMBE % | 0.563 | 0.682 |
| R² | 0.715 | 0.507 |

Skill vs same_time_last_week: **0.24** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 10.7% (limit 30%), NMBE 0.6% (limit ±10%): **passes**.

90% prediction interval: ±65.3 kWh (width from validation errors); it contained 77% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-21 to 2017-08-04 | 1732 | 0.30 |
| 2017-08-04 to 2017-10-19 | 1731 | 0.20 |
| 2017-10-19 to 2017-12-31 | 1731 | 0.26 |

Pooled skill: **0.25**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 70% |
| calendar (time of day, weekday) | 29% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
