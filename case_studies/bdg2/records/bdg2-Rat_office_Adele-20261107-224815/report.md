# Run report: bdg2-Rat_office_Adele

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
| train | 2016-01-01 00:00:00 | 2017-05-26 00:00:00 | 12260 |
| val | 2017-05-27 01:00:00 | 2017-09-13 11:00:00 | 2603 |
| test | 2017-09-14 12:00:00 | 2017-12-31 23:00:00 | 2604 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 104.868 | 39.857 | 36.298 | -0.050 | 0.515 |
| same_time_yesterday | baseline | 104.868 | 39.857 | 36.298 | -0.050 | 0.515 |
| ridge | ml | 117.292 | 70.909 | 40.599 | -5.666 | 0.393 |
| gbm_change | ml | 117.726 | 83.381 | 40.749 | -22.258 | 0.389 |
| gbm | ml | 219.307 | 209.158 | 75.909 | -67.522 | -1.121 |
| same_time_last_week | baseline | 240.713 | 129.395 | 83.319 | -8.747 | -1.555 |
| time_of_day_profile | baseline | 421.816 | 399.469 | 146.004 | -134.726 | -6.846 |
| time_of_week_profile | baseline | 421.908 | 399.633 | 146.036 | -134.723 | -6.850 |
| towt | baseline | 466.271 | 439.209 | 161.392 | -151.543 | -8.587 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 115.702 | 115.702 |
| MAE (kWh) | 68.577 | 68.577 |
| CV(RMSE) % | 21.339 | 21.339 |
| NMBE % | 0.151 | 0.151 |
| R² | 0.447 | 0.447 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 21.3% (limit 30%), NMBE 0.2% (limit ±10%): **passes**.

90% prediction interval: ±76.3 kWh (width from validation errors); it contained 74% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-26 to 2017-08-08 | 1752 | 0.00 |
| 2017-08-08 to 2017-10-20 | 1752 | 0.00 |
| 2017-10-20 to 2017-12-31 | 1751 | 0.00 |

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
