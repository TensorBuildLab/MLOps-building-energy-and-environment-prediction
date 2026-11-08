# Run report: bdg2-Crow_education_Omer

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 0.5 for 11 h (2017-01-03 13:00:00 to 2017-01-04 00:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 11.8, 0.5 at 2017-03-21 22:00:00. | prepare() treats them as missing (by default). |

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
| train | 2016-01-01 00:00:00 | 2017-04-20 05:00:00 | 11396 |
| val | 2017-04-21 06:00:00 | 2017-07-31 01:00:00 | 2418 |
| test | 2017-08-01 02:00:00 | 2017-11-09 21:00:00 | 2419 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 36.115 | 26.187 | 12.426 | -1.035 | 0.888 |
| gbm | ml | 36.511 | 25.486 | 12.562 | -3.790 | 0.886 |
| gbm_change | ml | 37.077 | 24.951 | 12.757 | -2.141 | 0.882 |
| same_time_last_week | baseline | 43.687 | 27.642 | 15.031 | -0.337 | 0.836 |
| same_time_yesterday | baseline | 61.195 | 35.748 | 21.055 | -0.339 | 0.679 |
| persistence | baseline | 61.195 | 35.748 | 21.055 | -0.339 | 0.679 |
| towt | baseline | 62.835 | 54.232 | 21.619 | -17.442 | 0.661 |
| time_of_week_profile | baseline | 66.856 | 58.849 | 23.002 | -19.115 | 0.616 |
| time_of_day_profile | baseline | 67.279 | 58.776 | 23.148 | -19.144 | 0.612 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 39.532 | 50.484 |
| MAE (kWh) | 27.758 | 33.468 |
| CV(RMSE) % | 11.663 | 14.894 |
| NMBE % | 0.182 | 1.362 |
| R² | 0.893 | 0.825 |

Skill vs same_time_last_week: **0.22** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 11.7% (limit 30%), NMBE 0.2% (limit ±10%): **passes**.

90% prediction interval: ±55.9 kWh (width from validation errors); it contained 88% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-04-20 to 2017-06-27 | 1629 | 0.18 |
| 2017-06-27 to 2017-09-03 | 1628 | 0.17 |
| 2017-09-03 to 2017-11-09 | 1628 | 0.23 |

Pooled skill: **0.20**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 77% |
| calendar (time of day, weekday) | 23% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
