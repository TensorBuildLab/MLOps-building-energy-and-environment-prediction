# Run report: bdg2-Fox_education_Stacia

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 79.13 for 3 d 2 h (2016-03-28 08:00:00 to 2016-03-31 10:00:00); 10 such stretch(es), 12 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10.6 for 9 h (2017-02-18 21:00:00 to 2017-02-19 06:00:00); 6 such stretch(es), 1 d 18 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 7 h (2017-08-26 00:00:00 to 2017-08-26 07:00:00); 1 such stretch(es), 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 10 stuck stretch(es) set to missing. (251)
- mask_stuck `airTemperature`: 6 stuck stretch(es) set to missing. (12)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (8)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (2)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (14)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-01 07:00:00 | 11963 |
| val | 2017-06-02 08:00:00 | 2017-09-16 02:00:00 | 2539 |
| test | 2017-09-17 03:00:00 | 2017-12-31 23:00:00 | 2541 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| time_of_day_profile | baseline | 2.834 | 1.817 | 3.669 | 1.209 | 0.433 |
| time_of_week_profile | baseline | 2.952 | 1.914 | 3.822 | 1.212 | 0.384 |
| same_time_last_week | baseline | 3.276 | 1.558 | 4.241 | 0.154 | 0.242 |
| ridge | ml | 3.288 | 2.265 | 4.257 | 1.801 | 0.236 |
| persistence | baseline | 3.813 | 1.915 | 4.936 | 0.023 | -0.027 |
| same_time_yesterday | baseline | 3.813 | 1.915 | 4.936 | 0.023 | -0.027 |
| towt | baseline | 7.791 | 6.580 | 10.087 | 8.183 | -3.290 |
| gbm | ml | 11.218 | 6.335 | 14.524 | 6.690 | -7.892 |
| gbm_change | ml | 12.155 | 6.873 | 15.737 | 7.552 | -9.440 |

## Test result

Chosen model: **time_of_day_profile** 

| Metric | Model | time_of_day_profile |
|---|---|---|
| RMSE (kWh) | 4.486 | 4.486 |
| MAE (kWh) | 3.359 | 3.359 |
| CV(RMSE) % | 5.666 | 5.666 |
| NMBE % | 3.469 | 3.469 |
| R² | 0.035 | 0.035 |

Skill vs time_of_day_profile: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 5.7% (limit 30%), NMBE 3.5% (limit ±10%): **passes**.

90% prediction interval: ±3.61 kWh (width from validation errors); it contained 61% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-01 to 2017-08-11 | 1710 | 0.00 |
| 2017-08-11 to 2017-10-21 | 1709 | 0.00 |
| 2017-10-21 to 2017-12-31 | 1709 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'time_of_day_profile' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
