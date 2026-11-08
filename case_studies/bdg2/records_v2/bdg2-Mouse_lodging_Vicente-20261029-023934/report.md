# Run report: bdg2-Mouse_lodging_Vicente

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 40.9238 for 8 d 22 h (2016-01-06 01:00:00 to 2016-01-14 23:00:00); 169 such stretch(es), 93 d 7 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 169 stuck stretch(es) set to missing. (1394)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-04-14 00:00:00 | 10145 |
| val | 2017-04-15 01:00:00 | 2017-07-24 00:00:00 | 2150 |
| test | 2017-07-25 01:00:00 | 2017-10-23 23:00:00 | 2151 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 8.571 | 6.521 | 18.159 | 1.985 | 0.706 |
| ridge | ml | 8.732 | 6.724 | 18.502 | 1.533 | 0.695 |
| gbm_change | ml | 8.850 | 6.628 | 18.750 | 3.023 | 0.687 |
| time_of_day_profile | baseline | 10.349 | 7.823 | 21.926 | 4.731 | 0.572 |
| persistence | baseline | 12.337 | 8.412 | 26.138 | 1.160 | 0.392 |
| same_time_yesterday | baseline | 12.337 | 8.412 | 26.138 | 1.160 | 0.392 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 7.682 | 7.688 |
| MAE (kWh) | 6.078 | 5.968 |
| CV(RMSE) % | 16.057 | 16.071 |
| NMBE % | -2.215 | 4.411 |
| R² | 0.741 | 0.740 |

Skill vs time_of_day_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 16.1% (limit 30%), NMBE -2.2% (limit ±10%): **passes**.

90% prediction interval: ±14.2 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-04-14 to 2017-06-22 | 1450 | 0.10 |
| 2017-06-22 to 2017-08-24 | 1450 | 0.21 |
| 2017-08-24 to 2017-10-23 | 1449 | -0.12 |

Pooled skill: **0.10**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 69% |
| calendar (time of day, weekday) | 31% |

> Warning: The model is barely better than time_of_day_profile on test data (skill 0.00).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
