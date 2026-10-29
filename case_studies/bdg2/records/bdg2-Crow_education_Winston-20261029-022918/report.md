# Run report: bdg2-Crow_education_Winston

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing. |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing. |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (165)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (209)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (170)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-01 03:00:00 | 11576 |
| val | 2017-05-02 04:00:00 | 2017-08-12 12:00:00 | 2456 |
| test | 2017-08-13 13:00:00 | 2017-11-23 22:00:00 | 2458 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 51.091 | 34.419 | 12.164 | 1.962 | 0.764 |
| persistence | baseline | 56.907 | 35.229 | 13.548 | 0.617 | 0.707 |
| same_time_yesterday | baseline | 56.907 | 35.229 | 13.548 | 0.617 | 0.707 |
| gbm_change | ml | 62.097 | 42.674 | 14.784 | 5.751 | 0.652 |
| gbm | ml | 68.805 | 48.060 | 16.381 | 6.490 | 0.572 |
| time_of_day_profile | baseline | 163.346 | 151.613 | 38.889 | 32.029 | -1.410 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(1.96282248134428)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 42.050 | 50.302 |
| MAE (kWh) | 30.317 | 31.674 |
| CV(RMSE) % | 11.831 | 14.153 |
| NMBE % | -1.772 | -0.403 |
| R² | 0.888 | 0.839 |

Skill vs persistence: **0.16** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.8% (limit 30%), NMBE -1.8% (limit ±10%): **passes**.

90% prediction interval: ±71 kWh (width from validation errors); it contained 92% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-01 to 2017-07-09 | 1654 | 0.07 |
| 2017-07-09 to 2017-09-16 | 1654 | 0.23 |
| 2017-09-16 to 2017-11-23 | 1654 | 0.12 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 89% |
| calendar (time of day, weekday) | 8% |
| airTemperature | 3% |
| windSpeed | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
