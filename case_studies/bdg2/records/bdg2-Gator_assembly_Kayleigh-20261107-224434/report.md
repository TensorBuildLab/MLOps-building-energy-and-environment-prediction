# Run report: bdg2-Gator_assembly_Kayleigh

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 2.1667 for 9 d 23 h (2016-12-18 00:00:00 to 2016-12-27 23:00:00); 513 such stretch(es), 629 d 15 h in total. The value is unchanged in 97% of steps and changes by at least ~0.1667 when it does: this looks like change-of-value logging with a deadband. | If so, flat stretches are normal: declare the column with flat_ok=True and note why. Otherwise prepare() treats them as missing. |
| warning | `stuck:airTemperature` | Sensor repeats exactly 23.9 for 12 h (2017-07-31 18:00:00 to 2017-08-01 06:00:00); 28 such stretch(es), 7 d 19 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 2.1 for 8 h (2017-06-11 23:00:00 to 2017-06-12 07:00:00); 3 such stretch(es), 20 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 513 stuck stretch(es) set to missing. (12546)
- mask_stuck `airTemperature`: 28 stuck stretch(es) set to missing. (47)
- mask_stuck `windSpeed`: 3 stuck stretch(es) set to missing. (5)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (29)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (1)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (3)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-22 05:00:00 | 2422 |
| val | 2017-05-25 00:00:00 | 2017-08-25 14:00:00 | 513 |
| test | 2017-08-27 00:00:00 | 2017-12-31 05:00:00 | 510 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 4.257 | 2.646 | 115.642 | -6.321 | 0.276 |
| gbm | ml | 4.552 | 2.408 | 123.636 | 31.770 | 0.172 |
| gbm_change | ml | 4.746 | 2.981 | 128.901 | 1.768 | 0.100 |
| towt | baseline | 4.845 | 3.865 | 131.590 | -6.753 | 0.062 |
| same_time_last_week | baseline | 5.275 | 3.519 | 143.289 | -38.056 | -0.112 |
| persistence | baseline | 5.742 | 3.699 | 155.961 | -35.218 | -0.317 |
| same_time_yesterday | baseline | 5.742 | 3.699 | 155.961 | -35.218 | -0.317 |
| time_of_week_profile | baseline | 6.080 | 4.828 | 165.135 | -83.576 | -0.477 |
| time_of_day_profile | baseline | 6.167 | 5.280 | 167.500 | -88.557 | -0.519 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 8.789 | 10.112 |
| MAE (kWh) | 6.727 | 7.696 |
| CV(RMSE) % | 74.904 | 86.182 |
| NMBE % | 25.783 | 46.248 |
| R² | 0.310 | 0.086 |

Skill vs towt: **0.13** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 74.9% (limit 30%), NMBE 25.8% (limit ±10%): **does not pass**.

90% prediction interval: ±5.32 kWh (width from validation errors); it contained 46% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-23 to 2017-07-29 | 346 | 0.06 |
| 2017-07-29 to 2017-10-03 | 346 | 0.20 |
| 2017-10-03 to 2017-12-31 | 346 | 0.14 |

Pooled skill: **0.13**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 85% |
| calendar (time of day, weekday) | 15% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
