# Run report: bdg2-Moose_education_Maria

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 568.484 for 3 d 11 h (2016-05-20 17:00:00 to 2016-05-24 04:00:00); 319 such stretch(es), 164 d 12 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 319 stuck stretch(es) set to missing. (2353)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (165)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (209)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (170)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-22 19:00:00 | 10551 |
| val | 2017-06-23 20:00:00 | 2017-09-25 01:00:00 | 2237 |
| test | 2017-09-26 02:00:00 | 2017-12-31 23:00:00 | 2238 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 6.198 | 2.726 | 0.653 | -0.009 | -0.255 |
| same_time_yesterday | baseline | 6.198 | 2.726 | 0.653 | -0.009 | -0.255 |
| same_time_last_week | baseline | 6.908 | 3.846 | 0.728 | -0.150 | -0.559 |
| gbm | ml | 39.985 | 26.741 | 4.214 | 0.767 | -51.237 |
| gbm_change | ml | 62.900 | 31.223 | 6.630 | 1.564 | -128.262 |
| ridge | ml | 77.614 | 62.603 | 8.180 | 5.018 | -195.814 |
| towt | baseline | 254.047 | 231.026 | 26.776 | 24.350 | -2107.638 |
| time_of_day_profile | baseline | 269.894 | 247.546 | 28.447 | 26.097 | -2378.906 |
| time_of_week_profile | baseline | 270.084 | 247.542 | 28.467 | 26.097 | -2382.270 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 31.362 | 31.362 |
| MAE (kWh) | 19.821 | 19.821 |
| CV(RMSE) % | 3.410 | 3.410 |
| NMBE % | 0.220 | 0.220 |
| R² | -1.828 | -1.828 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 3.4% (limit 30%), NMBE 0.2% (limit ±10%): **passes**.

90% prediction interval: ±6.03 kWh (width from validation errors); it contained 32% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-22 to 2017-08-24 | 1508 | 0.00 |
| 2017-08-24 to 2017-10-30 | 1508 | 0.00 |
| 2017-10-30 to 2017-12-31 | 1507 | 0.00 |

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
