# Run report: bdg2-Lamb_education_Princess

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 5.3 for 6 h (2016-08-12 01:00:00 to 2016-08-12 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10 for 1 d 18 h (2017-12-20 15:00:00 to 2017-12-22 09:00:00); 278 such stretch(es), 101 d 2 h in total. | prepare() treats these stretches as missing. |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3.1 for 7 h (2017-09-15 23:00:00 to 2017-09-16 06:00:00); 4 such stretch(es), 1 d 1 h in total. | prepare() treats these stretches as missing. |
| warning | `spikes:windSpeed` | 3 single-sample spike(s), e.g. 16, 12.9, 11.8 at 2016-03-28 04:00:00. | prepare() treats them as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 1 stuck stretch(es) set to missing. (1)
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
| train | 2016-01-01 00:00:00 | 2017-05-27 14:00:00 | 12228 |
| val | 2017-05-28 15:00:00 | 2017-09-13 18:00:00 | 2596 |
| test | 2017-09-14 19:00:00 | 2017-12-31 23:00:00 | 2597 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| same_time_yesterday | baseline | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| gbm | ml | 0.305 | 0.220 | 60974.089 | 12769.115 | -7903924474070975336303344970908041216.000 |
| gbm_change | ml | 0.402 | 0.242 | 80351.367 | 17966.269 | -13725831927602514246492319747584032768.000 |
| ridge | ml | 2.304 | 1.853 | 460880.957 | -106140.859 | -451574763841428936105394448363203592192.000 |
| time_of_day_profile | baseline | 10.490 | 8.608 | 2098384.964 | -1722211.994 | -9361004791063885919436687961360173105152.000 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 4.160 | 4.160 |
| MAE (kWh) | 1.068 | 1.068 |
| CV(RMSE) % | 99.003 | 99.003 |
| NMBE % | 1.396 | 1.396 |
| R² | 0.753 | 0.753 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 99.0% (limit 30%), NMBE 1.4% (limit ±10%): **does not pass**.

90% prediction interval: ±0 kWh (width from validation errors); it contained 69% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-08 | 1747 | nan |
| 2017-08-08 to 2017-10-20 | 1747 | nan |
| 2017-10-20 to 2017-12-31 | 1747 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 100% |

> Warning: No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
