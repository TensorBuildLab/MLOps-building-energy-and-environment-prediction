# Run report: bdg2-Bobcat_other_Howard

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -6.1 for 12 h (2017-01-01 16:00:00 to 2017-01-02 04:00:00); 19 such stretch(es), 5 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 4.1 for 6 h (2017-02-26 01:00:00 to 2017-02-26 07:00:00); 1 such stretch(es), 6 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 16.5, 14.9 at 2016-02-18 03:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `airTemperature`: 19 stuck stretch(es) set to missing. (38)
- mask_stuck `windSpeed`: 1 stuck stretch(es) set to missing. (1)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (35)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (16)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (122)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-06-07 18:00:00 | 11338 |
| val | 2017-06-08 19:00:00 | 2017-09-20 22:00:00 | 2406 |
| test | 2017-09-21 23:00:00 | 2017-12-31 23:00:00 | 2407 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 124.938 | 62.250 | 172.341 | -0.290 | 0.354 |
| gbm | ml | 127.481 | 63.710 | 175.849 | -2.508 | 0.327 |
| ridge | ml | 129.242 | 64.521 | 178.278 | 1.322 | 0.309 |
| towt | baseline | 139.374 | 71.029 | 192.255 | 12.446 | 0.196 |
| time_of_week_profile | baseline | 140.773 | 64.538 | 194.184 | 28.447 | 0.180 |
| time_of_day_profile | baseline | 143.475 | 65.482 | 197.912 | 28.375 | 0.148 |
| same_time_yesterday | baseline | 155.877 | 64.813 | 215.020 | -1.079 | -0.006 |
| persistence | baseline | 155.877 | 64.813 | 215.020 | -1.079 | -0.006 |
| same_time_last_week | baseline | 171.965 | 75.109 | 237.211 | 0.225 | -0.224 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 78.351 | 91.009 |
| MAE (kWh) | 34.363 | 47.720 |
| CV(RMSE) % | 234.072 | 271.889 |
| NMBE % | -21.329 | -30.544 |
| R² | -0.044 | -0.409 |

Skill vs towt: **0.14** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 234.1% (limit 30%), NMBE -21.3% (limit ±10%): **does not pass**.

90% prediction interval: ±156 kWh (width from validation errors); it contained 98% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-07 to 2017-08-17 | 1620 | 0.04 |
| 2017-08-17 to 2017-10-25 | 1620 | 0.10 |
| 2017-10-25 to 2017-12-31 | 1620 | 0.35 |

Pooled skill: **0.11**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 79% |
| calendar (time of day, weekday) | 13% |
| airTemperature | 6% |
| windSpeed | 2% |
| dewTemperature | 2% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
