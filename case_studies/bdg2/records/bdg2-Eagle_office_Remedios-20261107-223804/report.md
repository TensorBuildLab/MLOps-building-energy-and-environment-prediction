# Run report: bdg2-Eagle_office_Remedios

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 85.4137 for 2 d 13 h (2016-07-16 05:00:00 to 2016-07-18 18:00:00); 6 such stretch(es), 4 d 23 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 5 for 18 h (2017-01-20 12:00:00 to 2017-01-21 06:00:00); 43 such stretch(es), 13 d 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 7 h (2016-11-05 19:00:00 to 2016-11-06 02:00:00); 2 such stretch(es), 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 6 stuck stretch(es) set to missing. (89)
- mask_stuck `airTemperature`: 43 stuck stretch(es) set to missing. (103)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (47)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (40)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-22 15:00:00 | 11409 |
| val | 2017-05-23 16:00:00 | 2017-09-01 19:00:00 | 2420 |
| test | 2017-09-02 20:00:00 | 2017-12-31 23:00:00 | 2422 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 7.359 | 5.490 | 7.971 | 2.378 | 0.698 |
| time_of_week_profile | baseline | 7.371 | 5.533 | 7.984 | 4.557 | 0.697 |
| time_of_day_profile | baseline | 7.433 | 5.612 | 8.051 | 4.578 | 0.692 |
| towt | baseline | 7.509 | 5.711 | 8.133 | 4.814 | 0.686 |
| same_time_last_week | baseline | 8.131 | 5.802 | 8.807 | 0.154 | 0.632 |
| same_time_yesterday | baseline | 11.367 | 7.658 | 12.311 | 0.054 | 0.280 |
| persistence | baseline | 11.367 | 7.658 | 12.311 | 0.054 | 0.280 |
| gbm | ml | 12.522 | 7.608 | 13.562 | 5.560 | 0.126 |
| gbm_change | ml | 13.919 | 7.435 | 15.075 | 5.239 | -0.079 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | time_of_week_profile |
|---|---|---|
| RMSE (kWh) | 7.265 | 6.747 |
| MAE (kWh) | 5.205 | 4.818 |
| CV(RMSE) % | 7.995 | 7.425 |
| NMBE % | 0.400 | 2.514 |
| R² | 0.695 | 0.737 |

Skill vs time_of_week_profile: **-0.08** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 8.0% (limit 30%), NMBE 0.4% (limit ±10%): **passes**.

90% prediction interval: ±11.2 kWh (width from validation errors); it contained 91% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-22 to 2017-07-29 | 1630 | -0.00 |
| 2017-07-29 to 2017-10-05 | 1630 | -0.02 |
| 2017-10-05 to 2017-12-31 | 1630 | -0.12 |

Pooled skill: **-0.04**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 60% |
| calendar (time of day, weekday) | 40% |

> Warning: The model is barely better than time_of_week_profile on test data (skill -0.08).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
