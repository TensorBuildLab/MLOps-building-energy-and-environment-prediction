# Run report: bdg2-Bear_education_Destiny

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 14.4 for 11 h (2016-08-05 21:00:00 to 2016-08-06 08:00:00); 52 such stretch(es), 15 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-09-24 01:00:00 to 2017-09-24 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 1 single-sample spike(s), e.g. 16.5 at 2017-02-20 20:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 52 stuck stretch(es) set to missing. (101)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (54)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (4)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-15 09:00:00 | 11175 |
| val | 2017-06-16 10:00:00 | 2017-09-23 03:00:00 | 2370 |
| test | 2017-09-24 04:00:00 | 2017-12-31 23:00:00 | 2372 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 20.674 | 14.869 | 18.216 | -4.536 | 0.831 |
| gbm | ml | 20.919 | 15.727 | 18.432 | -6.144 | 0.827 |
| ridge | ml | 20.975 | 15.108 | 18.481 | -3.829 | 0.826 |
| persistence | baseline | 25.073 | 17.035 | 22.092 | -0.099 | 0.751 |
| same_time_yesterday | baseline | 25.073 | 17.035 | 22.092 | -0.099 | 0.751 |
| same_time_last_week | baseline | 29.587 | 20.573 | 26.069 | -0.920 | 0.653 |
| time_of_week_profile | baseline | 31.216 | 26.378 | 27.505 | -17.390 | 0.614 |
| time_of_day_profile | baseline | 31.261 | 26.379 | 27.544 | -17.394 | 0.613 |
| towt | baseline | 41.464 | 37.446 | 36.534 | -31.126 | 0.319 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 15.404 | 21.611 |
| MAE (kWh) | 11.195 | 14.521 |
| CV(RMSE) % | 15.240 | 21.381 |
| NMBE % | -4.149 | -0.282 |
| R² | 0.867 | 0.739 |

Skill vs persistence: **0.29** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 15.2% (limit 30%), NMBE -4.1% (limit ±10%): **passes**.

90% prediction interval: ±29.1 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-15 to 2017-08-20 | 1597 | 0.18 |
| 2017-08-20 to 2017-10-26 | 1597 | 0.21 |
| 2017-10-26 to 2017-12-31 | 1596 | 0.26 |

Pooled skill: **0.21**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 78% |
| calendar (time of day, weekday) | 22% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
