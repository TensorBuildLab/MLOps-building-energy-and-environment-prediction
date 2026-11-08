# Run report: bdg2-Wolf_education_Cody

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3 for 14 h (2016-11-02 19:00:00 to 2016-11-03 09:00:00); 51 such stretch(es), 14 d 10 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `windSpeed`: 51 stuck stretch(es) set to missing. (90)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (20)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (20)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (70)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 19:00:00 | 12268 |
| val | 2017-05-27 20:00:00 | 2017-09-13 08:00:00 | 2604 |
| test | 2017-09-14 09:00:00 | 2017-12-31 23:00:00 | 2606 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 19.724 | 13.516 | 94.220 | -15.829 | 0.099 |
| ridge | ml | 20.046 | 14.760 | 95.755 | -20.297 | 0.069 |
| time_of_day_profile | baseline | 20.167 | 14.291 | 96.335 | -17.335 | 0.058 |
| time_of_week_profile | baseline | 20.351 | 14.356 | 97.213 | -17.078 | 0.041 |
| towt | baseline | 20.477 | 14.483 | 97.816 | -18.422 | 0.029 |
| gbm | ml | 20.574 | 14.183 | 98.280 | -17.785 | 0.019 |
| same_time_yesterday | baseline | 25.246 | 14.513 | 120.594 | -0.090 | -0.476 |
| persistence | baseline | 25.246 | 14.513 | 120.594 | -0.090 | -0.476 |
| same_time_last_week | baseline | 26.984 | 16.194 | 128.899 | -1.888 | -0.687 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 50, 'base__max_leaf_nodes': 7, 'base__max_iter': 100, 'base__learning_rate': 0.2, 'base__l2_regularization': 1.0}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 21.773 | 23.105 |
| MAE (kWh) | 14.960 | 15.359 |
| CV(RMSE) % | 82.009 | 87.026 |
| NMBE % | -4.951 | 9.859 |
| R² | 0.370 | 0.290 |

Skill vs time_of_day_profile: **0.06** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 82.0% (limit 30%), NMBE -5.0% (limit ±10%): **does not pass**.

90% prediction interval: ±32.9 kWh (width from validation errors); it contained 89% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1753 | -0.01 |
| 2017-08-07 to 2017-10-19 | 1753 | -0.03 |
| 2017-10-19 to 2017-12-31 | 1752 | 0.07 |

Pooled skill: **0.02**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 67% |
| electricity (recent history) | 32% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
