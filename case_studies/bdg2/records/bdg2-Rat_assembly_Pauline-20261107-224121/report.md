# Run report: bdg2-Rat_assembly_Pauline

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 0.96 for 10 h (2017-05-25 20:00:00 to 2017-05-26 06:00:00); 52 such stretch(es), 14 d 14 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly 18.3 for 11 h (2016-10-01 20:00:00 to 2016-10-02 07:00:00); 51 such stretch(es), 15 d 2 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 1.5 for 6 h (2016-08-07 22:00:00 to 2016-08-08 04:00:00); 2 such stretch(es), 12 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 52 stuck stretch(es) set to missing. (87)
- mask_stuck `airTemperature`: 51 stuck stretch(es) set to missing. (107)
- mask_stuck `windSpeed`: 2 stuck stretch(es) set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (60)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (12)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (16)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-24 22:00:00 | 11865 |
| val | 2017-05-25 23:00:00 | 2017-09-11 19:00:00 | 2521 |
| test | 2017-09-12 20:00:00 | 2017-12-31 23:00:00 | 2520 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| ridge | ml | 0.967 | 0.667 | 41.252 | -2.353 | 0.778 |
| persistence | baseline | 1.031 | 0.597 | 43.949 | -0.014 | 0.748 |
| same_time_yesterday | baseline | 1.031 | 0.597 | 43.949 | -0.014 | 0.748 |
| gbm_change | ml | 1.321 | 0.915 | 56.341 | -29.183 | 0.586 |
| gbm | ml | 1.358 | 0.934 | 57.894 | -30.391 | 0.563 |
| same_time_last_week | baseline | 1.501 | 0.905 | 64.028 | 1.329 | 0.466 |
| towt | baseline | 1.591 | 1.257 | 67.862 | -26.033 | 0.400 |
| time_of_day_profile | baseline | 1.792 | 1.266 | 76.437 | 20.981 | 0.239 |
| time_of_week_profile | baseline | 1.793 | 1.266 | 76.457 | 20.990 | 0.238 |

## Test result

Chosen model: **ridge** {'model__alpha': np.float64(19.549524484259873)}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 0.538 | 0.598 |
| MAE (kWh) | 0.287 | 0.246 |
| CV(RMSE) % | 61.091 | 67.870 |
| NMBE % | -13.539 | -5.587 |
| R² | 0.330 | 0.173 |

Skill vs persistence: **0.10** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 61.1% (limit 30%), NMBE -13.5% (limit ±10%): **does not pass**.

90% prediction interval: ±1.6 kWh (width from validation errors); it contained 97% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-25 to 2017-08-07 | 1696 | 0.06 |
| 2017-08-07 to 2017-10-17 | 1695 | 0.06 |
| 2017-10-17 to 2017-12-31 | 1695 | 0.23 |

Pooled skill: **0.07**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 96% |
| dewTemperature | 3% |
| calendar (time of day, weekday) | 1% |

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
