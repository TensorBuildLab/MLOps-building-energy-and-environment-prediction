# Run report: bdg2-Bear_education_Rebecca

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
| train | 2016-01-01 00:00:00 | 2017-05-25 14:00:00 | 12243 |
| val | 2017-05-26 15:00:00 | 2017-09-11 21:00:00 | 2599 |
| test | 2017-09-12 22:00:00 | 2017-12-31 23:00:00 | 2601 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 37.981 | 27.150 | 5.347 | -1.495 | 0.751 |
| persistence | baseline | 42.669 | 28.205 | 6.007 | 0.112 | 0.685 |
| same_time_yesterday | baseline | 42.669 | 28.205 | 6.007 | 0.112 | 0.685 |
| gbm | ml | 52.060 | 41.988 | 7.329 | -4.005 | 0.532 |
| same_time_last_week | baseline | 58.031 | 39.277 | 8.169 | 0.567 | 0.418 |
| gbm_change | ml | 59.857 | 46.907 | 8.426 | -4.646 | 0.381 |
| time_of_day_profile | baseline | 106.760 | 97.381 | 15.029 | -13.003 | -0.969 |
| time_of_week_profile | baseline | 106.865 | 97.364 | 15.044 | -12.991 | -0.973 |
| towt | baseline | 120.658 | 111.770 | 16.986 | -15.500 | -1.515 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 35.987 | 44.044 |
| MAE (kWh) | 26.977 | 31.062 |
| CV(RMSE) % | 4.791 | 5.863 |
| NMBE % | -1.134 | -0.059 |
| R² | 0.772 | 0.659 |

Skill vs persistence: **0.18** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 4.8% (limit 30%), NMBE -1.1% (limit ±10%): **passes**.

90% prediction interval: ±54.7 kWh (width from validation errors); it contained 89% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-06 | 1750 | 0.17 |
| 2017-08-06 to 2017-10-18 | 1749 | 0.12 |
| 2017-10-18 to 2017-12-31 | 1749 | 0.17 |

Pooled skill: **0.15**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 76% |
| calendar (time of day, weekday) | 19% |
| airTemperature | 4% |
| windSpeed | 1% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
