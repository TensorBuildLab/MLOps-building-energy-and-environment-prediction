# Run report: bdg2-Lamb_assembly_Delilah

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 2 for 13 h (2016-11-27 18:00:00 to 2016-11-28 07:00:00); 41 such stretch(es), 12 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 10 for 1 d 18 h (2017-12-20 15:00:00 to 2017-12-22 09:00:00); 278 such stretch(es), 101 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 3.1 for 7 h (2017-09-15 23:00:00 to 2017-09-16 06:00:00); 4 such stretch(es), 1 d 1 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 3 single-sample spike(s), e.g. 16, 12.9, 11.8 at 2016-03-28 04:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 41 stuck stretch(es) set to missing. (84)
- mask_stuck `airTemperature`: 278 stuck stretch(es) set to missing. (1035)
- mask_stuck `windSpeed`: 4 stuck stretch(es) set to missing. (5)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (3)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (299)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (24)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (31)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-28 06:00:00 | 12189 |
| val | 2017-05-29 07:00:00 | 2017-09-14 02:00:00 | 2588 |
| test | 2017-09-15 03:00:00 | 2017-12-31 23:00:00 | 2589 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| same_time_yesterday | baseline | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| same_time_last_week | baseline | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| gbm | ml | 0.438 | 0.294 | 218956.853 | -92360.912 | -260920780618672710282071400741001494528.000 |
| ridge | ml | 0.956 | 0.783 | 477857.003 | 103828.475 | -1242760654371640379901918388721087938560.000 |
| gbm_change | ml | 1.184 | 0.409 | 592334.006 | -154126.312 | -1909523104259493182533801894868800241664.000 |
| time_of_day_profile | baseline | 11.326 | 9.281 | 5663906.677 | -4642167.708 | -174591767736890739209900976901549002326016.000 |
| time_of_week_profile | baseline | 11.474 | 9.294 | 5738128.933 | -4648799.985 | -179197600118642297026965109883037328343040.000 |
| towt | baseline | 15.836 | 12.668 | 7919452.438 | -6326902.378 | -341335842257543232657436774196022859530240.000 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.000 | 0.000 |
| MAE (kWh) | 0.000 | 0.000 |
| CV(RMSE) % | 0.000 | 0.000 |
| NMBE % | 0.000 | 0.000 |
| R² | 1.000 | 1.000 |

Skill vs persistence: **nan** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 0.0% (limit 30%), NMBE 0.0% (limit ±10%): **passes**.

90% prediction interval: ±0 kWh (width from validation errors); it contained 100% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-28 to 2017-08-08 | 1742 | nan |
| 2017-08-08 to 2017-10-20 | 1742 | nan |
| 2017-10-20 to 2017-12-31 | 1741 | nan |

Pooled skill: **nan**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

> Warning: No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
