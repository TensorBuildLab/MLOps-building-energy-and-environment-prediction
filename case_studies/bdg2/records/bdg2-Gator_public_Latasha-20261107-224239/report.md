# Run report: bdg2-Gator_public_Latasha

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 16.6667 for 6 d 23 h (2017-12-19 00:00:00 to 2017-12-25 23:00:00); 513 such stretch(es), 632 d 15 h in total. The value is unchanged in 97% of steps and changes by at least ~0.4167 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 513 stuck stretch(es) set to missing. (12618)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-08 02:00:00 | 2456 |
| val | 2017-05-09 03:00:00 | 2017-08-15 00:00:00 | 520 |
| test | 2017-08-16 01:00:00 | 2017-12-30 05:00:00 | 521 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| time_of_day_profile | baseline | 5.406 | 3.816 | 27.618 | 9.057 | 0.484 |
| time_of_week_profile | baseline | 5.497 | 3.882 | 28.084 | 9.072 | 0.467 |
| gbm | ml | 5.823 | 3.985 | 29.749 | -8.283 | 0.402 |
| towt | baseline | 5.906 | 3.865 | 30.172 | -4.459 | 0.384 |
| ridge | ml | 6.169 | 4.105 | 31.514 | -5.276 | 0.328 |
| gbm_change | ml | 8.127 | 5.688 | 41.521 | -8.107 | -0.166 |
| same_time_yesterday | baseline | 8.527 | 6.044 | 43.563 | -5.252 | -0.283 |
| persistence | baseline | 8.527 | 6.044 | 43.563 | -5.252 | -0.283 |
| same_time_last_week | baseline | 8.651 | 6.215 | 44.196 | -3.555 | -0.321 |

## Test result

Chosen model: **time_of_day_profile** 

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 5.496 | 5.496 |
| MAE (kWh) | 4.314 | 4.314 |
| CV(RMSE) % | 32.854 | 32.854 |
| NMBE % | -11.805 | -11.805 |
| R² | 0.195 | 0.195 |

Skill vs time_of_day_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 32.9% (limit 30%), NMBE -11.8% (limit ±10%): **does not pass**.

90% prediction interval: ±5.7 kWh (width from validation errors); it contained 74% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-08 to 2017-07-18 | 351 | 0.00 |
| 2017-07-19 to 2017-09-24 | 351 | 0.00 |
| 2017-09-24 to 2017-12-30 | 351 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
