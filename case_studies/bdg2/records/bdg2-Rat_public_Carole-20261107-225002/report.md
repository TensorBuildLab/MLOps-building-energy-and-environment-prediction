# Run report: bdg2-Rat_public_Carole

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
| train | 2016-01-01 00:00:00 | 2017-05-25 18:00:00 | 12215 |
| val | 2017-05-26 19:00:00 | 2017-09-12 20:00:00 | 2593 |
| test | 2017-09-13 21:00:00 | 2017-12-31 23:00:00 | 2594 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| towt | baseline | 4.062 | 3.146 | 17.917 | -4.167 | 0.388 |
| ridge | ml | 4.134 | 3.227 | 18.234 | -0.706 | 0.367 |
| gbm_change | ml | 4.375 | 3.397 | 19.297 | -7.361 | 0.291 |
| gbm | ml | 4.420 | 3.429 | 19.496 | -7.511 | 0.276 |
| same_time_yesterday | baseline | 4.698 | 3.524 | 20.723 | 0.170 | 0.182 |
| persistence | baseline | 4.698 | 3.524 | 20.723 | 0.170 | 0.182 |
| same_time_last_week | baseline | 6.054 | 4.771 | 26.702 | 0.207 | -0.359 |
| time_of_day_profile | baseline | 6.467 | 5.407 | 28.522 | 18.342 | -0.550 |
| time_of_week_profile | baseline | 6.469 | 5.412 | 28.530 | 18.337 | -0.551 |

## Test result

Chosen model: **towt** 

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 3.331 | 3.331 |
| MAE (kWh) | 2.589 | 2.589 |
| CV(RMSE) % | 20.399 | 20.399 |
| NMBE % | -7.738 | -7.738 |
| R² | 0.258 | 0.258 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 20.4% (limit 30%), NMBE -7.7% (limit ±10%): **passes**.

90% prediction interval: ±6.81 kWh (width from validation errors); it contained 96% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-07 | 1745 | 0.00 |
| 2017-08-07 to 2017-10-20 | 1745 | 0.00 |
| 2017-10-20 to 2017-12-31 | 1745 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| airTemperature | 100% |

> Warning: No machine-learning model beat the 'towt' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
