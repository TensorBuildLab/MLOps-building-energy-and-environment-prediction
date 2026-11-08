# Run report: bdg2-Robin_lodging_Celia

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

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
| gbm | ml | 7.007 | 3.541 | 17.176 | -3.134 | 0.648 |
| gbm_change | ml | 7.060 | 3.590 | 17.307 | -1.981 | 0.642 |
| ridge | ml | 7.617 | 4.113 | 18.670 | -1.633 | 0.584 |
| persistence | baseline | 8.193 | 4.102 | 20.084 | -0.391 | 0.518 |
| same_time_yesterday | baseline | 8.193 | 4.102 | 20.084 | -0.391 | 0.518 |
| same_time_last_week | baseline | 10.697 | 5.701 | 26.222 | -3.280 | 0.179 |
| towt | baseline | 13.731 | 9.637 | 33.660 | -12.442 | -0.353 |
| time_of_week_profile | baseline | 17.134 | 12.616 | 42.001 | -29.679 | -1.107 |
| time_of_day_profile | baseline | 17.144 | 12.595 | 42.025 | -29.644 | -1.109 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 4.979 | 6.399 |
| MAE (kWh) | 3.575 | 4.416 |
| CV(RMSE) % | 9.193 | 11.814 |
| NMBE % | -0.441 | 0.199 |
| R² | 0.936 | 0.894 |

Skill vs persistence: **0.22** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 9.2% (limit 30%), NMBE -0.4% (limit ±10%): **passes**.

90% prediction interval: ±6.35 kWh (width from validation errors); it contained 84% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.07 |
| 2017-08-07 to 2017-10-19 | 1755 | 0.22 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.25 |

Pooled skill: **0.17**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 92% |
| calendar (time of day, weekday) | 8% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
