# Run report: bdg2-Gator_public_Dewey

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 5.0833 for 1 d 23 h (2016-03-01 00:00:00 to 2016-03-02 23:00:00); 653 such stretch(es), 640 d 19 h in total. The value is unchanged in 96% of steps and changes by at least ~0.0834 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 653 stuck stretch(es) set to missing. (12114)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-28 05:00:00 | 3010 |
| val | 2017-05-30 00:00:00 | 2017-09-21 02:00:00 | 639 |
| test | 2017-09-23 00:00:00 | 2017-12-31 05:00:00 | 642 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 1.243 | 0.816 | 16.714 | 4.659 | -0.029 |
| gbm_change | ml | 1.317 | 0.901 | 17.703 | 3.458 | -0.154 |
| gbm | ml | 1.326 | 0.893 | 17.827 | 4.653 | -0.170 |
| towt | baseline | 1.334 | 0.886 | 17.931 | 6.067 | -0.184 |
| same_time_yesterday | baseline | 1.471 | 0.868 | 19.768 | 1.051 | -0.439 |
| persistence | baseline | 1.471 | 0.868 | 19.768 | 1.051 | -0.439 |
| same_time_last_week | baseline | 1.750 | 1.105 | 23.521 | 1.347 | -1.037 |
| time_of_day_profile | baseline | 1.785 | 1.575 | 23.992 | 17.535 | -1.120 |
| time_of_week_profile | baseline | 1.791 | 1.575 | 24.071 | 17.532 | -1.134 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(1.96282248134428)}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 1.321 | 1.136 |
| MAE (kWh) | 0.819 | 0.656 |
| CV(RMSE) % | 23.237 | 19.982 |
| NMBE % | 1.059 | 1.989 |
| R² | 0.556 | 0.672 |

Skill vs towt: **-0.16** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 23.2% (limit 30%), NMBE 1.1% (limit ±10%): **passes**.

90% prediction interval: ±1.75 kWh (width from validation errors); it contained 92% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-29 to 2017-08-14 | 430 | 0.10 |
| 2017-08-14 to 2017-10-30 | 430 | -0.02 |
| 2017-10-30 to 2017-12-31 | 430 | -0.20 |

Pooled skill: **-0.04**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| calendar (time of day, weekday) | 80% |
| dewTemperature | 15% |
| electricity (recent history) | 4% |

> Warning: The model is barely better than towt on test data (skill -0.16).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
