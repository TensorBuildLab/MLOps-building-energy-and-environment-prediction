# Run report: bdg2-Lamb_education_Freddy

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 1.4 for 10 h (2016-10-28 08:00:00 to 2016-10-28 18:00:00); 14 such stretch(es), 3 d 22 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10 for 1 d 18 h (2017-12-20 15:00:00 to 2017-12-22 09:00:00); 278 such stretch(es), 101 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3.1 for 7 h (2017-09-15 23:00:00 to 2017-09-16 06:00:00); 4 such stretch(es), 1 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 3 single-sample spike(s), e.g. 16, 12.9, 11.8 at 2016-03-28 04:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 14 stuck stretch(es) set to missing. (24)
- mask_stuck `airTemperature`: 278 stuck stretch(es) set to missing. (1035)
- mask_stuck `windSpeed`: 4 stuck stretch(es) set to missing. (5)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (299)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (24)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (31)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-28 03:00:00 | 12197 |
| val | 2017-05-29 04:00:00 | 2017-09-14 00:00:00 | 2589 |
| test | 2017-09-15 01:00:00 | 2017-12-31 23:00:00 | 2591 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| same_time_yesterday | baseline | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| same_time_last_week | baseline | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| gbm_change | ml | 0.657 | 0.458 | 657348.267 | -430655.767 | -587926049397188964706464390597746622464.000 |
| gbm | ml | 0.906 | 0.565 | 905784.883 | -513305.413 | -1116302235709402688625726421167209709568.000 |
| ridge | ml | 1.027 | 0.823 | 1027229.531 | -308317.739 | -1435709751085196523642825461087667748864.000 |
| towt | baseline | 4.014 | 3.299 | 4015098.230 | -3300600.045 | -21934311539781368436195409298178594308096.000 |
| time_of_day_profile | baseline | 4.554 | 3.908 | 4554485.931 | -3909452.825 | -28223468668401126337700081254409990832128.000 |
| time_of_week_profile | baseline | 4.567 | 3.912 | 4567740.410 | -3913981.396 | -28387979756209384609134074654511100592128.000 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.000 | 0.000 |
| MAE (kWh) | 0.000 | 0.000 |
| CV(RMSE) % | 0.000 | 0.000 |
| NMBE % | 0.000 | 0.000 |
| R² | 1.000 | 1.000 |

Skill vs persistence: **nan** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 0.0% (limit 30%), NMBE 0.0% (limit ±10%): **passes**.

90% prediction interval: ±0 kWh (width from validation errors); it contained 100% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-28 to 2017-08-08 | 1743 | nan |
| 2017-08-08 to 2017-10-20 | 1743 | nan |
| 2017-10-20 to 2017-12-31 | 1742 | nan |

Pooled skill: **nan**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
