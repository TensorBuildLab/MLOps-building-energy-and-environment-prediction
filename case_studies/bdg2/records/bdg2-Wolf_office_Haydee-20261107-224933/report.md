# Run report: bdg2-Wolf_office_Haydee

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
| gbm_change | ml | 3.892 | 2.358 | 53.403 | 0.477 | 0.477 |
| gbm | ml | 3.958 | 2.430 | 54.315 | 0.549 | 0.459 |
| ridge | ml | 4.254 | 2.902 | 58.372 | -2.453 | 0.375 |
| towt | baseline | 4.545 | 2.893 | 62.363 | -3.836 | 0.287 |
| time_of_day_profile | baseline | 4.775 | 3.598 | 65.514 | -21.817 | 0.213 |
| time_of_week_profile | baseline | 4.815 | 3.616 | 66.072 | -21.862 | 0.199 |
| same_time_yesterday | baseline | 5.031 | 3.050 | 69.028 | 0.221 | 0.126 |
| persistence | baseline | 5.031 | 3.050 | 69.028 | 0.221 | 0.126 |
| same_time_last_week | baseline | 6.235 | 3.673 | 85.550 | 0.554 | -0.343 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 3.685 | 4.640 |
| MAE (kWh) | 2.439 | 3.214 |
| CV(RMSE) % | 42.214 | 53.160 |
| NMBE % | -4.138 | -3.695 |
| R² | 0.677 | 0.488 |

Skill vs towt: **0.21** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 42.2% (limit 30%), NMBE -4.1% (limit ±10%): **does not pass**.

90% prediction interval: ±6 kWh (width from validation errors); it contained 90% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1755 | 0.12 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.16 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.23 |

Pooled skill: **0.17**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 54% |
| electricity (recent history) | 44% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
