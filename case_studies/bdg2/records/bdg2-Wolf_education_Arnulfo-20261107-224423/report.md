# Run report: bdg2-Wolf_education_Arnulfo

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
| train | 2016-01-01 00:00:00 | 2017-05-31 07:00:00 | 12014 |
| val | 2017-06-01 08:00:00 | 2017-09-15 14:00:00 | 2550 |
| test | 2017-09-16 15:00:00 | 2017-12-31 23:00:00 | 2552 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 12.382 | 8.021 | 39.030 | -0.128 | 0.354 |
| gbm_change | ml | 12.517 | 8.053 | 39.455 | 0.579 | 0.340 |
| ridge | ml | 13.404 | 9.720 | 42.250 | -1.674 | 0.243 |
| persistence | baseline | 14.868 | 8.958 | 46.865 | 0.242 | 0.069 |
| same_time_yesterday | baseline | 14.868 | 8.958 | 46.865 | 0.242 | 0.069 |
| towt | baseline | 14.970 | 10.509 | 47.187 | -4.376 | 0.056 |
| time_of_day_profile | baseline | 15.903 | 12.222 | 50.127 | -15.643 | -0.065 |
| time_of_week_profile | baseline | 15.961 | 12.257 | 50.310 | -15.639 | -0.073 |
| same_time_last_week | baseline | 19.696 | 12.268 | 62.083 | 2.059 | -0.634 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 100, 'max_leaf_nodes': 15, 'max_iter': 100, 'learning_rate': 0.1, 'l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 10.812 | 16.068 |
| MAE (kWh) | 7.216 | 9.635 |
| CV(RMSE) % | 28.621 | 42.536 |
| NMBE % | -1.977 | -0.231 |
| R² | 0.617 | 0.154 |

Skill vs persistence: **0.33** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 28.6% (limit 30%), NMBE -2.0% (limit ±10%): **passes**.

90% prediction interval: ±21.2 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-31 to 2017-08-10 | 1717 | 0.14 |
| 2017-08-10 to 2017-10-21 | 1717 | 0.30 |
| 2017-10-21 to 2017-12-31 | 1716 | 0.30 |

Pooled skill: **0.25**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 56% |
| electricity (recent history) | 43% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
