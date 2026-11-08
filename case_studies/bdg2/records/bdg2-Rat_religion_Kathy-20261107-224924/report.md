# Run report: bdg2-Rat_religion_Kathy

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 18.3 for 11 h (2016-10-01 20:00:00 to 2016-10-02 07:00:00); 51 such stretch(es), 15 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2016-08-07 22:00:00 to 2016-08-08 04:00:00); 2 such stretch(es), 12 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 51 stuck stretch(es) set to missing. (107)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (60)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (12)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (16)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-25 05:00:00 | 12240 |
| val | 2017-05-26 06:00:00 | 2017-09-13 12:00:00 | 2599 |
| test | 2017-09-14 13:00:00 | 2017-12-31 23:00:00 | 2600 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 1.920 | 1.507 | 36.213 | -13.367 | 0.341 |
| ridge | ml | 1.924 | 1.514 | 36.289 | -4.681 | 0.338 |
| gbm | ml | 1.940 | 1.542 | 36.587 | -14.046 | 0.327 |
| towt | baseline | 1.982 | 1.566 | 37.392 | -14.659 | 0.297 |
| time_of_day_profile | baseline | 2.100 | 1.716 | 39.614 | 0.638 | 0.211 |
| time_of_week_profile | baseline | 2.105 | 1.721 | 39.709 | 0.620 | 0.208 |
| same_time_yesterday | baseline | 2.258 | 1.699 | 42.594 | 0.024 | 0.088 |
| persistence | baseline | 2.258 | 1.699 | 42.594 | 0.024 | 0.088 |
| same_time_last_week | baseline | 2.531 | 1.905 | 47.737 | -0.056 | -0.145 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 1.812 | 1.816 |
| MAE (kWh) | 1.433 | 1.444 |
| CV(RMSE) % | 39.986 | 40.075 |
| NMBE % | -8.588 | -10.131 |
| R² | 0.260 | 0.257 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 40.0% (limit 30%), NMBE -8.6% (limit ±10%): **does not pass**.

90% prediction interval: ±3.13 kWh (width from validation errors); it contained 92% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-08 | 1749 | 0.03 |
| 2017-08-08 to 2017-10-20 | 1749 | 0.00 |
| 2017-10-20 to 2017-12-31 | 1749 | 0.01 |

Pooled skill: **0.01**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 51% |
| electricity (recent history) | 35% |
| airTemperature | 13% |
| dewTemperature | 1% |
| windSpeed | 1% |

> Warning: The model is barely better than towt on test data (skill 0.00).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
