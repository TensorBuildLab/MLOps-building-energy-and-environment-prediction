# Run report: bdg2-Bear_education_Zandra

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
| train | 2016-01-01 00:00:00 | 2017-05-25 13:00:00 | 12203 |
| val | 2017-05-26 14:00:00 | 2017-09-12 10:00:00 | 2591 |
| test | 2017-09-13 11:00:00 | 2017-12-31 23:00:00 | 2592 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 42.780 | 26.382 | 4.482 | -0.695 | 0.710 |
| persistence | baseline | 48.942 | 25.923 | 5.128 | 0.158 | 0.620 |
| same_time_yesterday | baseline | 48.942 | 25.923 | 5.128 | 0.158 | 0.620 |
| gbm | ml | 49.657 | 37.350 | 5.203 | -1.887 | 0.609 |
| gbm_change | ml | 54.156 | 39.901 | 5.674 | -2.276 | 0.535 |
| same_time_last_week | baseline | 76.383 | 38.526 | 8.003 | 0.017 | 0.074 |
| time_of_week_profile | baseline | 82.784 | 75.475 | 8.674 | -4.315 | -0.088 |
| time_of_day_profile | baseline | 82.830 | 75.568 | 8.678 | -4.317 | -0.089 |
| towt | baseline | 94.749 | 88.155 | 9.927 | -6.218 | -0.425 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 20.823 | 27.081 |
| MAE (kWh) | 16.674 | 17.497 |
| CV(RMSE) % | 2.256 | 2.934 |
| NMBE % | -0.712 | -0.094 |
| R² | 0.689 | 0.475 |

Skill vs persistence: **0.23** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 2.3% (limit 30%), NMBE -0.7% (limit ±10%): **passes**.

90% prediction interval: ±53.2 kWh (width from validation errors); it contained 99% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-07 | 1744 | 0.13 |
| 2017-08-07 to 2017-10-18 | 1744 | 0.22 |
| 2017-10-18 to 2017-12-31 | 1743 | 0.24 |

Pooled skill: **0.16**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 54% |
| calendar (time of day, weekday) | 46% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
