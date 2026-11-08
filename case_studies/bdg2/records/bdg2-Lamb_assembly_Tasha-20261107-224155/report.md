# Run report: bdg2-Lamb_assembly_Tasha

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10 for 1 d 18 h (2017-12-20 15:00:00 to 2017-12-22 09:00:00); 278 such stretch(es), 101 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3.1 for 7 h (2017-09-15 23:00:00 to 2017-09-16 06:00:00); 4 such stretch(es), 1 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 3 single-sample spike(s), e.g. 16, 12.9, 11.8 at 2016-03-28 04:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

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
| train | 2016-01-01 00:00:00 | 2017-05-26 22:00:00 | 12264 |
| val | 2017-05-27 23:00:00 | 2017-09-13 10:00:00 | 2604 |
| test | 2017-09-14 11:00:00 | 2017-12-31 23:00:00 | 2605 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 0.000 | 0.000 | 0.000 | 0.000 | nan |
| same_time_yesterday | baseline | 0.000 | 0.000 | 0.000 | 0.000 | nan |
| same_time_last_week | baseline | 0.000 | 0.000 | 0.000 | 0.000 | nan |
| gbm | ml | 0.362 | 0.265 | 30209.798 | -17189.872 | nan |
| gbm_change | ml | 0.575 | 0.444 | 47922.717 | -27539.319 | nan |
| ridge | ml | 1.029 | 0.934 | 85757.160 | -77688.553 | nan |
| time_of_day_profile | baseline | 12.178 | 12.136 | 1015002.071 | -1011741.334 | nan |
| time_of_week_profile | baseline | 12.178 | 12.136 | 1015063.689 | -1011746.167 | nan |
| towt | baseline | 25.842 | 24.883 | 2153905.728 | -2074364.258 | nan |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 3.153 | 3.153 |
| MAE (kWh) | 1.090 | 1.090 |
| CV(RMSE) % | 73.895 | 73.895 |
| NMBE % | 1.138 | 1.138 |
| R² | 0.793 | 0.793 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 73.9% (limit 30%), NMBE 1.1% (limit ±10%): **does not pass**.

90% prediction interval: ±0 kWh (width from validation errors); it contained 55% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1753 | nan |
| 2017-08-08 to 2017-10-19 | 1752 | nan |
| 2017-10-20 to 2017-12-31 | 1752 | 0.00 |

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
