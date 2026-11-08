# Run report: bdg2-Bear_education_Derek

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 14.4 for 11 h (2016-08-05 21:00:00 to 2016-08-06 08:00:00); 52 such stretch(es), 15 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-09-24 01:00:00 to 2017-09-24 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 1 single-sample spike(s), e.g. 16.5 at 2017-02-20 20:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 52 stuck stretch(es) set to missing. (101)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (54)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (5)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (4)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-26 17:00:00 | 12232 |
| val | 2017-05-27 18:00:00 | 2017-09-13 09:00:00 | 2598 |
| test | 2017-09-14 10:00:00 | 2017-12-31 23:00:00 | 2598 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 9.736 | 7.572 | 5.071 | 1.303 | 0.734 |
| gbm_change | ml | 10.098 | 7.800 | 5.260 | 2.304 | 0.714 |
| gbm | ml | 10.391 | 8.011 | 5.412 | 2.227 | 0.697 |
| persistence | baseline | 10.970 | 8.348 | 5.714 | 0.181 | 0.662 |
| same_time_yesterday | baseline | 10.970 | 8.348 | 5.714 | 0.181 | 0.662 |
| towt | baseline | 12.303 | 9.773 | 6.408 | 3.925 | 0.575 |
| same_time_last_week | baseline | 12.573 | 9.834 | 6.549 | 0.563 | 0.557 |
| time_of_day_profile | baseline | 14.041 | 11.020 | 7.314 | 4.729 | 0.447 |
| time_of_week_profile | baseline | 14.249 | 11.163 | 7.422 | 4.727 | 0.431 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 22.674 | 24.051 |
| MAE (kWh) | 10.512 | 11.336 |
| CV(RMSE) % | 12.427 | 13.181 |
| NMBE % | -0.990 | -0.375 |
| R² | 0.639 | 0.594 |

Skill vs persistence: **0.06** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 12.4% (limit 30%), NMBE -1.0% (limit ±10%): **passes**.

90% prediction interval: ±16 kWh (width from validation errors); it contained 89% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1748 | 0.14 |
| 2017-08-08 to 2017-10-19 | 1748 | 0.15 |
| 2017-10-19 to 2017-12-31 | 1747 | 0.05 |

Pooled skill: **0.07**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 95% |
| calendar (time of day, weekday) | 5% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
