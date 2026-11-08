# Run report: bdg2-Wolf_education_Dorris

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
| train | 2016-01-01 00:00:00 | 2017-05-26 15:00:00 | 12279 |
| val | 2017-05-27 16:00:00 | 2017-09-13 06:00:00 | 2607 |
| test | 2017-09-14 07:00:00 | 2017-12-31 23:00:00 | 2608 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 39.476 | 26.923 | 12.043 | 3.666 | 0.597 |
| gbm | ml | 39.959 | 27.127 | 12.190 | 4.113 | 0.587 |
| ridge | ml | 41.266 | 31.265 | 12.589 | 3.827 | 0.559 |
| time_of_day_profile | baseline | 42.060 | 29.577 | 12.831 | 4.242 | 0.542 |
| time_of_week_profile | baseline | 42.161 | 29.624 | 12.862 | 4.238 | 0.540 |
| towt | baseline | 43.334 | 30.934 | 13.220 | 5.339 | 0.514 |
| same_time_yesterday | baseline | 51.299 | 31.400 | 15.650 | 0.162 | 0.319 |
| persistence | baseline | 51.299 | 31.400 | 15.650 | 0.162 | 0.319 |
| same_time_last_week | baseline | 52.140 | 33.782 | 15.906 | 0.492 | 0.297 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 32.695 | 50.372 |
| MAE (kWh) | 23.801 | 39.779 |
| CV(RMSE) % | 9.837 | 15.156 |
| NMBE % | 2.278 | 4.783 |
| R² | 0.745 | 0.394 |

Skill vs time_of_day_profile: **0.35** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 9.8% (limit 30%), NMBE 2.3% (limit ±10%): **passes**.

90% prediction interval: ±60.9 kWh (width from validation errors); it contained 92% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.07 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.13 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.41 |

Pooled skill: **0.23**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 54% |
| electricity (recent history) | 45% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
