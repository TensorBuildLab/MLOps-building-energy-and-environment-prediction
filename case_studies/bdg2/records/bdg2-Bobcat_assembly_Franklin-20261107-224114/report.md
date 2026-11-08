# Run report: bdg2-Bobcat_assembly_Franklin

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
| train | 2016-01-01 00:00:00 | 2017-06-11 09:00:00 | 11352 |
| val | 2017-06-12 10:00:00 | 2017-09-20 19:00:00 | 2408 |
| test | 2017-09-21 20:00:00 | 2017-12-31 23:00:00 | 2410 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 77.914 | 55.942 | 42.469 | 5.178 | 0.566 |
| gbm | ml | 79.882 | 57.872 | 43.541 | 3.461 | 0.544 |
| ridge | ml | 81.045 | 60.921 | 44.176 | 2.699 | 0.530 |
| towt | baseline | 97.144 | 78.910 | 52.951 | 0.837 | 0.325 |
| time_of_week_profile | baseline | 99.917 | 75.196 | 54.462 | 12.108 | 0.286 |
| same_time_yesterday | baseline | 102.960 | 61.073 | 56.121 | 0.288 | 0.242 |
| persistence | baseline | 102.960 | 61.073 | 56.121 | 0.288 | 0.242 |
| time_of_day_profile | baseline | 103.203 | 79.267 | 56.253 | 11.991 | 0.239 |
| same_time_last_week | baseline | 106.293 | 70.692 | 57.937 | 1.416 | 0.192 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 100, 'base__max_leaf_nodes': 15, 'base__max_iter': 100, 'base__learning_rate': 0.1, 'base__l2_regularization': 1.0}

| Metric | Model | towt |
|---|---|---|
| RMSE (kWh) | 55.402 | 69.297 |
| MAE (kWh) | 36.926 | 58.928 |
| CV(RMSE) % | 48.088 | 60.149 |
| NMBE % | -6.880 | -33.379 |
| R² | 0.215 | -0.228 |

Skill vs towt: **0.20** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 48.1% (limit 30%), NMBE -6.9% (limit ±10%): **does not pass**.

90% prediction interval: ±135 kWh (width from validation errors); it contained 95% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-11 to 2017-08-18 | 1622 | 0.26 |
| 2017-08-18 to 2017-10-24 | 1622 | 0.15 |
| 2017-10-24 to 2017-12-31 | 1622 | 0.16 |

Pooled skill: **0.20**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 54% |
| calendar (time of day, weekday) | 45% |
| dewTemperature | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
