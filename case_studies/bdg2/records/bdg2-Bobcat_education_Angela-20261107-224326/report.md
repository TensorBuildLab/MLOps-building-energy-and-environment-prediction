# Run report: bdg2-Bobcat_education_Angela

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
| train | 2016-01-01 00:00:00 | 2017-06-08 15:00:00 | 11536 |
| val | 2017-06-09 16:00:00 | 2017-09-19 17:00:00 | 2448 |
| test | 2017-09-20 18:00:00 | 2017-12-31 23:00:00 | 2449 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| persistence | baseline | 14.354 | 7.743 | 18.111 | 0.183 | 0.467 |
| same_time_yesterday | baseline | 14.354 | 7.743 | 18.111 | 0.183 | 0.467 |
| ridge | ml | 15.117 | 8.671 | 19.075 | 1.648 | 0.409 |
| gbm_change | ml | 18.054 | 10.739 | 22.780 | -4.192 | 0.157 |
| gbm | ml | 18.828 | 12.080 | 23.757 | -4.710 | 0.083 |
| towt | baseline | 19.051 | 11.662 | 24.039 | -1.012 | 0.062 |
| time_of_day_profile | baseline | 19.283 | 13.456 | 24.331 | -7.544 | 0.039 |
| time_of_week_profile | baseline | 19.512 | 13.552 | 24.620 | -7.586 | 0.016 |
| same_time_last_week | baseline | 22.366 | 11.789 | 28.221 | 0.821 | -0.293 |

## Test result

Chosen model: **persistence** 

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 16.637 | 16.637 |
| MAE (kWh) | 10.242 | 10.242 |
| CV(RMSE) % | 18.138 | 18.138 |
| NMBE % | -0.083 | -0.083 |
| R² | 0.338 | 0.338 |

Skill vs persistence: **0.00** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 18.1% (limit 30%), NMBE -0.1% (limit ±10%): **passes**.

90% prediction interval: ±18.3 kWh (width from validation errors); it contained 84% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-06-08 to 2017-08-16 | 1649 | 0.00 |
| 2017-08-16 to 2017-10-24 | 1648 | 0.00 |
| 2017-10-24 to 2017-12-31 | 1648 | 0.00 |

Pooled skill: **0.00**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 100% |

> Warning: No machine-learning model beat the 'persistence' baseline on validation data. Look for better inputs before deploying anything more complex.

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
