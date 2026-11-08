# Run report: bdg2-Gator_other_Reginald

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 58.3333 for 4 d 23 h (2016-10-18 00:00:00 to 2016-10-22 23:00:00); 539 such stretch(es), 625 d 13 h in total. The value is unchanged in 97% of steps and changes by at least ~1.6667 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 539 stuck stretch(es) set to missing. (12318)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 00:00:00 | 2615 |
| val | 2017-05-28 00:00:00 | 2017-09-04 02:00:00 | 555 |
| test | 2017-09-05 03:00:00 | 2017-12-28 05:00:00 | 555 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| towt | baseline | 14.403 | 8.880 | 23.117 | -4.278 | 0.514 |
| ridge | ml | 15.970 | 10.129 | 25.632 | -7.478 | 0.402 |
| gbm | ml | 16.873 | 13.040 | 27.082 | -15.234 | 0.333 |
| time_of_week_profile | baseline | 18.428 | 15.420 | 29.577 | 19.755 | 0.204 |
| time_of_day_profile | baseline | 19.409 | 15.915 | 31.152 | 19.420 | 0.117 |
| gbm_change | ml | 20.520 | 13.572 | 32.936 | -11.852 | 0.013 |
| same_time_last_week | baseline | 20.682 | 14.658 | 33.194 | -0.164 | -0.002 |
| persistence | baseline | 22.025 | 16.054 | 35.351 | -0.352 | -0.137 |
| same_time_yesterday | baseline | 22.025 | 16.054 | 35.351 | -0.352 | -0.137 |

## Test result

Chosen model: **towt** 

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 15.169 | 15.169 |
| MAE (kWh) | 10.435 | 10.435 |
| CV(RMSE) % | 35.146 | 35.146 |
| NMBE % | -16.979 | -16.979 |
| R² | 0.314 | 0.314 |

Skill vs towt: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 35.1% (limit 30%), NMBE -17.0% (limit ±10%): **does not pass**.

90% prediction interval: ±17.2 kWh (width from validation errors); it contained 84% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-05 | 374 | 0.00 |
| 2017-08-05 to 2017-10-14 | 374 | 0.00 |
| 2017-10-14 to 2017-12-28 | 373 | 0.00 |

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
