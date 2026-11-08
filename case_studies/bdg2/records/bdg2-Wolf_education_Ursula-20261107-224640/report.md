# Run report: bdg2-Wolf_education_Ursula

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 101.54 for 23 h (2017-07-10 00:00:00 to 2017-07-10 23:00:00); 11 such stretch(es), 4 d 18 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3 for 14 h (2016-11-02 19:00:00 to 2016-11-03 09:00:00); 51 such stretch(es), 14 d 10 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 11 stuck stretch(es) set to missing. (59)
- mask_stuck `windSpeed`: 51 stuck stretch(es) set to missing. (90)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (20)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (20)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (70)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-25 00:00:00 | 12238 |
| val | 2017-05-26 01:00:00 | 2017-09-13 09:00:00 | 2598 |
| test | 2017-09-14 10:00:00 | 2017-12-31 23:00:00 | 2599 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 36.490 | 27.218 | 28.505 | -10.956 | 0.446 |
| ridge | ml | 36.913 | 28.321 | 28.835 | -10.147 | 0.433 |
| gbm | ml | 37.737 | 28.196 | 29.479 | -11.991 | 0.408 |
| towt | baseline | 39.586 | 31.008 | 30.924 | -14.548 | 0.348 |
| time_of_day_profile | baseline | 39.980 | 31.578 | 31.231 | -15.235 | 0.335 |
| time_of_week_profile | baseline | 39.997 | 31.574 | 31.245 | -15.203 | 0.335 |
| same_time_yesterday | baseline | 44.914 | 30.722 | 35.085 | -0.614 | 0.161 |
| persistence | baseline | 44.914 | 30.722 | 35.085 | -0.614 | 0.161 |
| same_time_last_week | baseline | 45.957 | 30.449 | 35.900 | -0.251 | 0.122 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 31.211 | 42.004 |
| MAE (kWh) | 21.704 | 32.045 |
| CV(RMSE) % | 25.211 | 33.930 |
| NMBE % | -7.370 | -17.604 |
| R² | 0.635 | 0.339 |

Skill vs towt: **0.26** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 25.2% (limit 30%), NMBE -7.4% (limit ±10%): **passes**.

90% prediction interval: ±58.1 kWh (width from validation errors); it contained 93% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-07 | 1749 | 0.07 |
| 2017-08-07 to 2017-10-20 | 1748 | 0.09 |
| 2017-10-20 to 2017-12-31 | 1748 | 0.31 |

Pooled skill: **0.17**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 60% |
| electricity (recent history) | 39% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
