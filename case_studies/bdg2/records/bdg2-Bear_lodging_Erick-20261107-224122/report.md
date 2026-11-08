# Run report: bdg2-Bear_lodging_Erick

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 14.4 for 11 h (2016-08-05 21:00:00 to 2016-08-06 08:00:00); 52 such stretch(es), 15 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-09-24 01:00:00 to 2017-09-24 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 1 single-sample spike(s), e.g. 16.5 at 2017-02-20 20:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 52 stuck stretch(es) set to missing. (101)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (54)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (4)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-25 14:00:00 | 12253 |
| val | 2017-05-26 15:00:00 | 2017-09-11 23:00:00 | 2601 |
| test | 2017-09-13 00:00:00 | 2017-12-31 23:00:00 | 2603 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 4.917 | 3.639 | 13.333 | -1.726 | 0.739 |
| ridge | ml | 4.941 | 3.643 | 13.396 | -0.447 | 0.736 |
| gbm | ml | 5.101 | 3.833 | 13.830 | -1.752 | 0.719 |
| persistence | baseline | 5.187 | 3.626 | 14.065 | 0.008 | 0.709 |
| same_time_yesterday | baseline | 5.187 | 3.626 | 14.065 | 0.008 | 0.709 |
| same_time_last_week | baseline | 10.241 | 7.684 | 27.768 | 1.126 | -0.134 |
| towt | baseline | 10.408 | 7.483 | 28.221 | -11.428 | -0.171 |
| time_of_week_profile | baseline | 15.862 | 13.654 | 43.007 | -36.519 | -1.719 |
| time_of_day_profile | baseline | 15.873 | 13.648 | 43.037 | -36.501 | -1.723 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 5.989 | 6.174 |
| MAE (kWh) | 4.491 | 4.616 |
| CV(RMSE) % | 11.555 | 11.912 |
| NMBE % | -1.616 | 0.118 |
| R² | 0.789 | 0.776 |

Skill vs persistence: **0.03** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.6% (limit 30%), NMBE -1.6% (limit ±10%): **passes**.

90% prediction interval: ±7.46 kWh (width from validation errors); it contained 83% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-06 | 1751 | 0.05 |
| 2017-08-06 to 2017-10-18 | 1751 | 0.08 |
| 2017-10-18 to 2017-12-31 | 1750 | 0.02 |

Pooled skill: **0.04**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 87% |
| calendar (time of day, weekday) | 10% |
| dewTemperature | 2% |
| windSpeed | 1% |

> Warning: The model is barely better than persistence on test data (skill 0.03).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
