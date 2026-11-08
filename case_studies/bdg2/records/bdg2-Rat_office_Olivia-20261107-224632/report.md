# Run report: bdg2-Rat_office_Olivia

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
| train | 2016-01-01 00:00:00 | 2017-05-25 06:00:00 | 12244 |
| val | 2017-05-26 07:00:00 | 2017-09-13 13:00:00 | 2599 |
| test | 2017-09-14 14:00:00 | 2017-12-31 23:00:00 | 2601 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 11.116 | 8.104 | 16.641 | 3.564 | 0.853 |
| gbm_change | ml | 12.051 | 8.721 | 18.040 | 4.735 | 0.827 |
| gbm | ml | 12.191 | 9.174 | 18.250 | 4.603 | 0.823 |
| same_time_last_week | baseline | 12.253 | 8.251 | 18.343 | 1.308 | 0.821 |
| towt | baseline | 14.990 | 13.377 | 22.440 | 17.529 | 0.733 |
| time_of_day_profile | baseline | 20.757 | 19.246 | 31.073 | 27.619 | 0.487 |
| time_of_week_profile | baseline | 20.793 | 19.195 | 31.127 | 27.671 | 0.485 |
| persistence | baseline | 23.480 | 13.062 | 35.149 | 0.887 | 0.344 |
| same_time_yesterday | baseline | 23.480 | 13.062 | 35.149 | 0.887 | 0.344 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | same_time_last_week |
|---|---|---|
| RMSE (kWh) | 11.040 | 12.334 |
| MAE (kWh) | 7.855 | 8.233 |
| CV(RMSE) % | 18.895 | 21.110 |
| NMBE % | 2.380 | -0.904 |
| R² | 0.769 | 0.711 |

Skill vs same_time_last_week: **0.10** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 18.9% (limit 30%), NMBE 2.4% (limit ±10%): **passes**.

90% prediction interval: ±17.7 kWh (width from validation errors); it contained 92% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-08 | 1750 | 0.11 |
| 2017-08-08 to 2017-10-20 | 1749 | 0.06 |
| 2017-10-20 to 2017-12-31 | 1749 | 0.12 |

Pooled skill: **0.10**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 82% |
| calendar (time of day, weekday) | 16% |
| dewTemperature | 2% |
| airTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
