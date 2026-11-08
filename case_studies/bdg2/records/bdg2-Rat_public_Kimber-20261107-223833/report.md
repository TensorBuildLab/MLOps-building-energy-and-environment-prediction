# Run report: bdg2-Rat_public_Kimber

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
| train | 2016-01-01 00:00:00 | 2017-05-26 16:00:00 | 12278 |
| val | 2017-05-27 17:00:00 | 2017-09-13 07:00:00 | 2607 |
| test | 2017-09-14 08:00:00 | 2017-12-31 23:00:00 | 2607 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 68.190 | 46.899 | 43.032 | -12.353 | 0.425 |
| gbm_change | ml | 70.377 | 47.412 | 44.412 | -14.587 | 0.387 |
| same_time_yesterday | baseline | 76.894 | 46.217 | 48.525 | -0.194 | 0.268 |
| persistence | baseline | 76.894 | 46.217 | 48.525 | -0.194 | 0.268 |
| gbm | ml | 77.463 | 55.334 | 48.884 | -22.259 | 0.257 |
| same_time_last_week | baseline | 97.824 | 64.889 | 61.734 | -4.369 | -0.184 |
| time_of_day_profile | baseline | 142.421 | 121.553 | 89.877 | -68.305 | -1.510 |
| time_of_week_profile | baseline | 142.535 | 121.399 | 89.949 | -68.247 | -1.514 |
| towt | baseline | 259.196 | 234.609 | 163.570 | -145.444 | -7.314 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(1.96282248134428)}

| Metric | Model | same_time_yesterday |
|---|---|---|
| RMSE (kWh) | 39.160 | 44.424 |
| MAE (kWh) | 28.853 | 29.816 |
| CV(RMSE) % | 34.733 | 39.402 |
| NMBE % | 0.722 | -0.705 |
| R² | 0.403 | 0.231 |

Skill vs same_time_yesterday: **0.12** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 34.7% (limit 30%), NMBE 0.7% (limit ±10%): **does not pass**.

90% prediction interval: ±99.7 kWh (width from validation errors); it contained 97% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-07 | 1754 | 0.13 |
| 2017-08-07 to 2017-10-19 | 1754 | 0.11 |
| 2017-10-19 to 2017-12-31 | 1754 | 0.12 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 77% |
| calendar (time of day, weekday) | 22% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
