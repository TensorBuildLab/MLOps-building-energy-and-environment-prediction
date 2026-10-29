# Run report: bdg2-Rat_education_Colin

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 18.3 for 11 h (2016-10-01 20:00:00 to 2016-10-02 07:00:00); 51 such stretch(es), 15 d 2 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2016-08-07 22:00:00 to 2016-08-08 04:00:00); 2 such stretch(es), 12 h in total. | prepare() treats these stretches as missing. |

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
| train | 2016-01-01 00:00:00 | 2017-05-24 13:00:00 | 12227 |
| val | 2017-05-25 14:00:00 | 2017-09-13 17:00:00 | 2596 |
| test | 2017-09-14 18:00:00 | 2017-12-31 23:00:00 | 2597 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm | ml | 11.579 | 8.153 | 17.219 | -3.087 | 0.528 |
| ridge | ml | 11.650 | 8.678 | 17.325 | -0.251 | 0.522 |
| gbm_change | ml | 11.934 | 8.211 | 17.747 | -3.384 | 0.499 |
| persistence | baseline | 11.938 | 6.781 | 17.752 | 0.460 | 0.499 |
| same_time_yesterday | baseline | 11.938 | 6.781 | 17.752 | 0.460 | 0.499 |
| time_of_day_profile | baseline | 21.488 | 18.226 | 31.954 | 12.006 | -0.625 |

## Test result

Chosen model: **gbm** {'min_samples_leaf': 20, 'max_leaf_nodes': 15, 'max_iter': 200, 'learning_rate': 0.05, 'l2_regularization': 0.1}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 26.342 | 4.283 |
| MAE (kWh) | 21.927 | 2.268 |
| CV(RMSE) % | 134.824 | 21.921 |
| NMBE % | -110.495 | -2.843 |
| R² | -2.627 | 0.904 |

Skill vs persistence: **-5.15** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 134.8% (limit 30%), NMBE -110.5% (limit ±10%): **does not pass**.

90% prediction interval: ±18.1 kWh (width from validation errors); it contained 37% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-24 to 2017-08-08 | 1747 | 0.16 |
| 2017-08-08 to 2017-10-20 | 1747 | -1.78 |
| 2017-10-20 to 2017-12-31 | 1747 | -5.28 |

Pooled skill: **-0.89**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 66% |
| calendar (time of day, weekday) | 13% |
| dewTemperature | 11% |
| airTemperature | 10% |

> Warning: The model is barely better than persistence on test data (skill -5.15).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
