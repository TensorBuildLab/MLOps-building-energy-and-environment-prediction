# Run report: bdg2-Wolf_education_Miguel

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
| train | 2016-01-01 00:00:00 | 2017-05-26 17:00:00 | 12274 |
| val | 2017-05-27 18:00:00 | 2017-09-13 07:00:00 | 2606 |
| test | 2017-09-14 08:00:00 | 2017-12-31 23:00:00 | 2607 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 10.931 | 6.371 | 31.398 | 2.654 | 0.534 |
| time_of_day_profile | baseline | 11.162 | 6.383 | 32.063 | -0.392 | 0.514 |
| gbm | ml | 11.200 | 6.623 | 32.173 | 3.951 | 0.511 |
| time_of_week_profile | baseline | 11.261 | 6.416 | 32.348 | -0.430 | 0.505 |
| towt | baseline | 11.335 | 6.501 | 32.562 | 3.309 | 0.499 |
| ridge | ml | 11.734 | 8.298 | 33.707 | 2.587 | 0.463 |
| same_time_last_week | baseline | 15.487 | 8.262 | 44.488 | -0.066 | 0.065 |
| persistence | baseline | 15.951 | 8.713 | 45.820 | 0.172 | 0.008 |
| same_time_yesterday | baseline | 15.951 | 8.713 | 45.820 | 0.172 | 0.008 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 10.540 | 12.798 |
| MAE (kWh) | 6.440 | 8.102 |
| CV(RMSE) % | 29.348 | 35.638 |
| NMBE % | 0.240 | 2.741 |
| R² | 0.673 | 0.518 |

Skill vs time_of_day_profile: **0.18** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 29.3% (limit 30%), NMBE 0.2% (limit ±10%): **passes**.

90% prediction interval: ±16.9 kWh (width from validation errors); it contained 90% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.05 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.05 |
| 2017-10-19 to 2017-12-31 | 1753 | 0.21 |

Pooled skill: **0.12**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 58% |
| electricity (recent history) | 41% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
