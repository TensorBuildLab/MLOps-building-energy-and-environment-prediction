# Run report: bdg2-Bull_education_Miranda

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 11.7 for 12 h (2017-10-31 20:00:00 to 2017-11-01 08:00:00); 59 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2017-06-19 23:00:00 to 2017-06-20 05:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 59 stuck stretch(es) set to missing. (144)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (80)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (28)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (218)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 01:00:00 | 2017-05-27 01:00:00 | 12049 |
| val | 2017-05-28 02:00:00 | 2017-09-11 18:00:00 | 2557 |
| test | 2017-09-12 19:00:00 | 2017-12-31 23:00:00 | 2559 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 13.407 | 9.516 | 8.266 | -1.092 | 0.556 |
| gbm | ml | 14.126 | 10.093 | 8.709 | -2.273 | 0.507 |
| gbm_change | ml | 14.127 | 9.993 | 8.709 | -2.064 | 0.507 |
| time_of_week_profile | baseline | 16.120 | 12.595 | 9.938 | -4.711 | 0.359 |
| time_of_day_profile | baseline | 16.247 | 12.676 | 10.017 | -4.721 | 0.348 |
| persistence | baseline | 16.789 | 11.117 | 10.351 | 0.140 | 0.304 |
| same_time_yesterday | baseline | 16.789 | 11.117 | 10.351 | 0.140 | 0.304 |
| towt | baseline | 19.063 | 15.406 | 11.753 | -7.050 | 0.103 |
| same_time_last_week | baseline | 19.064 | 13.401 | 11.753 | 0.228 | 0.103 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 23.042 | 25.215 |
| MAE (kWh) | 11.911 | 15.318 |
| CV(RMSE) % | 14.509 | 15.878 |
| NMBE % | -1.244 | -6.286 |
| R² | 0.322 | 0.188 |

Skill vs time_of_week_profile: **0.09** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 14.5% (limit 30%), NMBE -1.2% (limit ±10%): **passes**.

90% prediction interval: ±21.4 kWh (width from validation errors); it contained 88% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-27 to 2017-08-06 | 1722 | 0.17 |
| 2017-08-06 to 2017-10-17 | 1721 | 0.15 |
| 2017-10-17 to 2017-12-31 | 1721 | 0.07 |

Pooled skill: **0.11**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 61% |
| calendar (time of day, weekday) | 39% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
