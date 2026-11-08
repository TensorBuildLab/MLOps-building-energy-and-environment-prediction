# Run report: bdg2-Moose_education_Ricardo

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (165)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (209)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (170)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 12280 |
| val | 2017-05-27 16:00:00 | 2017-09-13 06:00:00 | 2607 |
| test | 2017-09-14 07:00:00 | 2017-12-31 23:00:00 | 2609 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 16.498 | 10.558 | 5.814 | 0.413 | 0.869 |
| gbm | ml | 17.470 | 11.464 | 6.157 | 0.647 | 0.854 |
| towt | baseline | 20.578 | 14.184 | 7.252 | 1.474 | 0.797 |
| ridge | ml | 20.747 | 14.092 | 7.311 | 0.572 | 0.793 |
| same_time_last_week | baseline | 23.650 | 15.113 | 8.335 | 0.313 | 0.732 |
| time_of_week_profile | baseline | 31.779 | 27.559 | 11.200 | -9.204 | 0.515 |
| time_of_day_profile | baseline | 32.159 | 27.649 | 11.333 | -9.201 | 0.504 |
| persistence | baseline | 38.062 | 22.303 | 13.414 | 0.143 | 0.305 |
| same_time_yesterday | baseline | 38.062 | 22.303 | 13.414 | 0.143 | 0.305 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 7, 'base__max_iter': 100, 'base__learning_rate': 0.2, 'base__l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 18.811 | 32.044 |
| MAE (kWh) | 13.180 | 25.290 |
| CV(RMSE) % | 5.735 | 9.769 |
| NMBE % | 0.682 | 5.888 |
| R² | 0.878 | 0.645 |

Skill vs towt: **0.41** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 5.7% (limit 30%), NMBE 0.7% (limit ±10%): **passes**.

90% prediction interval: ±21.1 kWh (width from validation errors); it contained 82% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.14 |
| 2017-08-07 to 2017-10-19 | 1755 | 0.30 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.49 |

Pooled skill: **0.35**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 67% |
| calendar (time of day, weekday) | 32% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
