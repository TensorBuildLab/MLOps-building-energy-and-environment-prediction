# Run report: bdg2-Rat_office_Rosemary

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
| train | 2016-01-01 00:00:00 | 2017-05-25 06:00:00 | 12243 |
| val | 2017-05-26 07:00:00 | 2017-09-13 13:00:00 | 2599 |
| test | 2017-09-14 14:00:00 | 2017-12-31 23:00:00 | 2601 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| towt | baseline | 4.207 | 3.279 | 24.901 | -8.052 | 0.716 |
| gbm_change | ml | 4.271 | 3.235 | 25.279 | -7.373 | 0.708 |
| gbm | ml | 4.335 | 3.291 | 25.660 | -8.990 | 0.699 |
| ridge | ml | 4.553 | 3.478 | 26.951 | -0.670 | 0.668 |
| time_of_week_profile | baseline | 4.918 | 3.858 | 29.110 | 2.736 | 0.612 |
| time_of_day_profile | baseline | 4.974 | 3.899 | 29.445 | 2.703 | 0.603 |
| same_time_last_week | baseline | 5.940 | 4.532 | 35.159 | -0.144 | 0.434 |
| persistence | baseline | 6.433 | 4.387 | 38.081 | -0.242 | 0.336 |
| same_time_yesterday | baseline | 6.433 | 4.387 | 38.081 | -0.242 | 0.336 |

## Test result

Chosen model: **towt** 

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 3.647 | 3.647 |
| MAE (kWh) | 2.819 | 2.819 |
| CV(RMSE) % | 21.968 | 21.968 |
| NMBE % | 4.720 | 4.720 |
| R² | 0.463 | 0.463 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 22.0% (limit 30%), NMBE 4.7% (limit ±10%): **passes**.

90% prediction interval: ±6.73 kWh (width from validation errors); it contained 94% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-08 | 1750 | 0.00 |
| 2017-08-08 to 2017-10-20 | 1749 | 0.00 |
| 2017-10-20 to 2017-12-31 | 1749 | 0.00 |

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
