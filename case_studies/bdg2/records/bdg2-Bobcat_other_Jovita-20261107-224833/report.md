# Run report: bdg2-Bobcat_other_Jovita

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 5 for 15 h (2016-10-17 19:00:00 to 2016-10-18 10:00:00); 51 such stretch(es), 16 d 15 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -6.1 for 12 h (2017-01-01 16:00:00 to 2017-01-02 04:00:00); 19 such stretch(es), 5 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 6 h (2017-02-26 01:00:00 to 2017-02-26 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 16.5, 14.9 at 2016-02-18 03:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 51 stuck stretch(es) set to missing. (144)
- mask_stuck `airTemperature`: 19 stuck stretch(es) set to missing. (38)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (35)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (122)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-09 15:00:00 | 11141 |
| val | 2017-06-10 16:00:00 | 2017-09-18 15:00:00 | 2363 |
| test | 2017-09-19 16:00:00 | 2017-12-31 23:00:00 | 2364 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 38.020 | 26.193 | 46.152 | 4.415 | 0.488 |
| gbm_change | ml | 42.386 | 29.955 | 51.451 | 5.487 | 0.363 |
| gbm | ml | 43.116 | 31.061 | 52.337 | 8.003 | 0.341 |
| persistence | baseline | 43.841 | 21.977 | 53.218 | 0.228 | 0.319 |
| same_time_yesterday | baseline | 43.841 | 21.977 | 53.218 | 0.228 | 0.319 |
| towt | baseline | 49.510 | 38.749 | 60.098 | 16.536 | 0.131 |
| same_time_last_week | baseline | 56.499 | 34.436 | 68.583 | -0.685 | -0.131 |
| time_of_week_profile | baseline | 76.125 | 63.117 | 92.406 | 67.797 | -1.054 |
| time_of_day_profile | baseline | 76.141 | 63.241 | 92.425 | 67.778 | -1.055 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 8.947 | 10.298 |
| MAE (kWh) | 6.107 | 4.347 |
| CV(RMSE) % | 98.086 | 112.895 |
| NMBE % | -19.745 | -16.454 |
| R² | 0.290 | 0.060 |

Skill vs persistence: **0.13** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 98.1% (limit 30%), NMBE -19.7% (limit ±10%): **does not pass**.

90% prediction interval: ±62.3 kWh (width from validation errors); it contained 100% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-09 to 2017-08-15 | 1592 | 0.10 |
| 2017-08-15 to 2017-10-23 | 1592 | 0.16 |
| 2017-10-23 to 2017-12-31 | 1591 | 0.23 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 80% |
| dewTemperature | 9% |
| airTemperature | 9% |
| windSpeed | 2% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
