# Run report: bdg2-Gator_assembly_Blanca

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 560.125 for 1 d 23 h (2016-01-05 00:00:00 to 2016-01-06 23:00:00); 688 such stretch(es), 663 d 8 h in total. The value is unchanged in 96% of steps and changes by at least ~12.25 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 688 stuck stretch(es) set to missing. (12480)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-31 05:00:00 | 3190 |
| val | 2017-06-02 00:00:00 | 2017-09-20 04:00:00 | 677 |
| test | 2017-09-21 05:00:00 | 2017-12-31 05:00:00 | 679 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| time_of_day_profile | baseline | 184.011 | 128.395 | 24.415 | 5.586 | 0.227 |
| time_of_week_profile | baseline | 186.965 | 131.602 | 24.807 | 5.630 | 0.202 |
| ridge | ml | 190.071 | 129.159 | 25.219 | -11.025 | 0.175 |
| gbm | ml | 201.497 | 152.443 | 26.735 | -4.629 | 0.073 |
| gbm_change | ml | 202.224 | 151.657 | 26.831 | -2.397 | 0.066 |
| towt | baseline | 208.068 | 148.008 | 27.607 | -14.496 | 0.011 |
| same_time_yesterday | baseline | 212.321 | 130.277 | 28.171 | -2.512 | -0.030 |
| persistence | baseline | 212.321 | 130.277 | 28.171 | -2.512 | -0.030 |
| same_time_last_week | baseline | 236.116 | 152.629 | 31.328 | -2.963 | -0.274 |

## Test result

Chosen model: **time_of_day_profile** 

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 187.671 | 187.671 |
| MAE (kWh) | 134.708 | 134.708 |
| CV(RMSE) % | 30.091 | 30.091 |
| NMBE % | -7.453 | -7.453 |
| R² | 0.466 | 0.466 |

Skill vs time_of_day_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 30.1% (limit 30%), NMBE -7.5% (limit ±10%): **does not pass**.

90% prediction interval: ±238 kWh (width from validation errors); it contained 87% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-01 to 2017-08-13 | 456 | 0.00 |
| 2017-08-14 to 2017-10-25 | 456 | 0.00 |
| 2017-10-26 to 2017-12-31 | 456 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
