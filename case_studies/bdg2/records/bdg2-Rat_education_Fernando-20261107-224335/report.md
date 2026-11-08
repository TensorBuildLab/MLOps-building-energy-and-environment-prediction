# Run report: bdg2-Rat_education_Fernando

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
| train | 2016-01-01 00:00:00 | 2017-05-25 13:00:00 | 12226 |
| val | 2017-05-26 14:00:00 | 2017-09-13 17:00:00 | 2596 |
| test | 2017-09-14 18:00:00 | 2017-12-31 23:00:00 | 2597 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 12.815 | 9.084 | 16.014 | 0.595 | 0.762 |
| gbm | ml | 13.469 | 9.819 | 16.831 | 1.010 | 0.737 |
| ridge | ml | 14.014 | 10.616 | 17.513 | 1.870 | 0.715 |
| towt | baseline | 16.535 | 13.130 | 20.662 | 8.802 | 0.604 |
| same_time_yesterday | baseline | 18.270 | 12.056 | 22.831 | 0.800 | 0.516 |
| persistence | baseline | 18.270 | 12.056 | 22.831 | 0.800 | 0.516 |
| same_time_last_week | baseline | 21.429 | 16.829 | 26.778 | 1.800 | 0.335 |
| time_of_week_profile | baseline | 28.593 | 23.922 | 35.731 | 26.366 | -0.184 |
| time_of_day_profile | baseline | 28.593 | 23.932 | 35.731 | 26.329 | -0.184 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 9.793 | 12.956 |
| MAE (kWh) | 6.935 | 9.533 |
| CV(RMSE) % | 16.323 | 21.593 |
| NMBE % | 1.002 | 4.973 |
| R² | 0.777 | 0.609 |

Skill vs towt: **0.24** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 16.3% (limit 30%), NMBE 1.0% (limit ±10%): **passes**.

90% prediction interval: ±19.3 kWh (width from validation errors); it contained 96% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-08 | 1747 | 0.17 |
| 2017-08-08 to 2017-10-20 | 1747 | 0.26 |
| 2017-10-20 to 2017-12-31 | 1747 | 0.26 |

Pooled skill: **0.22**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 65% |
| calendar (time of day, weekday) | 34% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
