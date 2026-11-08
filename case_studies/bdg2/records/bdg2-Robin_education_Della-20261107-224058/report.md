# Run report: bdg2-Robin_education_Della

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 3.5195 for 9 d 23 h (2017-08-05 00:00:00 to 2017-08-14 23:00:00); 89 such stretch(es), 67 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 7 h (2016-04-22 14:00:00 to 2016-04-22 21:00:00); 9 such stretch(es), 2 d 8 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 89 stuck stretch(es) set to missing. (1140)
- mask_stuck `windSpeed`: 9 stuck stretch(es) set to missing. (11)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (23)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-05 00:00:00 | 11413 |
| val | 2017-05-06 01:00:00 | 2017-08-31 18:00:00 | 2421 |
| test | 2017-09-01 19:00:00 | 2017-12-31 23:00:00 | 2423 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 1.261 | 0.933 | 30.331 | -3.219 | 0.654 |
| gbm | ml | 1.384 | 1.089 | 33.297 | -13.805 | 0.583 |
| ridge | ml | 1.390 | 1.035 | 33.438 | 3.511 | 0.579 |
| same_time_last_week | baseline | 1.624 | 1.111 | 39.071 | -1.206 | 0.425 |
| same_time_yesterday | baseline | 1.714 | 1.155 | 41.239 | 0.783 | 0.360 |
| persistence | baseline | 1.714 | 1.155 | 41.239 | 0.783 | 0.360 |
| time_of_week_profile | baseline | 2.226 | 1.697 | 53.554 | 39.140 | -0.080 |
| time_of_day_profile | baseline | 2.242 | 1.691 | 53.931 | 39.259 | -0.095 |
| towt | baseline | 3.478 | 3.124 | 83.675 | 75.087 | -1.637 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 7, 'base__max_iter': 100, 'base__learning_rate': 0.2, 'base__l2_regularization': 1.0}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 1.744 | 2.016 |
| MAE (kWh) | 1.248 | 1.404 |
| CV(RMSE) % | 35.592 | 41.142 |
| NMBE % | 2.525 | 5.647 |
| R² | 0.684 | 0.578 |

Skill vs same_time_last_week: **0.13** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 35.6% (limit 30%), NMBE 2.5% (limit ±10%): **does not pass**.

90% prediction interval: ±1.99 kWh (width from validation errors); it contained 81% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-05 to 2017-07-16 | 1631 | 0.20 |
| 2017-07-16 to 2017-10-10 | 1631 | 0.22 |
| 2017-10-10 to 2017-12-31 | 1630 | 0.12 |

Pooled skill: **0.16**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 69% |
| calendar (time of day, weekday) | 30% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
