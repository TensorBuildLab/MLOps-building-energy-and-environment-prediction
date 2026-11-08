# Run report: bdg2-Hog_office_Patrick

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 58 stuck stretch(es) set to missing. (149)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (62)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (11)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 17:00:00 | 12275 |
| val | 2017-05-27 18:00:00 | 2017-09-13 07:00:00 | 2606 |
| test | 2017-09-14 08:00:00 | 2017-12-31 23:00:00 | 2608 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 1.836 | 1.248 | 16.562 | -4.382 | 0.773 |
| time_of_week_profile | baseline | 1.938 | 1.356 | 17.481 | -1.019 | 0.747 |
| ridge | ml | 1.961 | 1.400 | 17.693 | 0.511 | 0.741 |
| time_of_day_profile | baseline | 1.992 | 1.397 | 17.972 | -0.965 | 0.733 |
| gbm | ml | 2.009 | 1.431 | 18.122 | -6.794 | 0.728 |
| same_time_last_week | baseline | 2.384 | 1.646 | 21.505 | 0.603 | 0.618 |
| persistence | baseline | 2.938 | 1.771 | 26.498 | 0.458 | 0.419 |
| same_time_yesterday | baseline | 2.938 | 1.771 | 26.498 | 0.458 | 0.419 |
| towt | baseline | 3.053 | 2.398 | 27.541 | -20.710 | 0.373 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 1.637 | 3.023 |
| MAE (kWh) | 1.078 | 2.420 |
| CV(RMSE) % | 18.114 | 33.456 |
| NMBE % | -2.803 | -23.589 |
| R² | 0.734 | 0.094 |

Skill vs time_of_week_profile: **0.46** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 18.1% (limit 30%), NMBE -2.8% (limit ±10%): **passes**.

90% prediction interval: ±2.64 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.06 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.27 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.49 |

Pooled skill: **0.32**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 61% |
| calendar (time of day, weekday) | 38% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
