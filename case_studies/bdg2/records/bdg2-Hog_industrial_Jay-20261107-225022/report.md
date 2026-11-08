# Run report: bdg2-Hog_industrial_Jay

**Task:** forecast electricity (energy, kWh) 1 d ahead (24 step(s) of 1 h)

## Data check

17544 raw rows from 2016-01-01 00:00:00 to 2017-12-31 23:00:00, typical step 1 h.

| Severity | Issue | What we found | What happens / what to do |
|---|---|---|---|
| info | `index:no_timezone` | Timestamps carry no time zone. | Fine if all are local time; check for daylight-saving jumps (Arizona and Hawaii have none). |
| warning | `stuck:electricity` | Sensor repeats exactly 267.38 for 6 d 14 h (2016-09-21 20:00:00 to 2016-09-28 10:00:00); 2 such stretch(es), 6 d 21 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:airTemperature` | Sensor repeats exactly -0.6 for 17 h (2016-01-06 17:00:00 to 2016-01-07 10:00:00); 58 such stretch(es), 18 d 7 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `stuck:windSpeed` | Sensor repeats exactly 7.7 for 9 h (2017-04-16 10:00:00 to 2017-04-16 19:00:00); 5 such stretch(es), 1 d 13 h in total. | prepare() treats these stretches as missing once they are detectable (by default). |
| warning | `spikes:windSpeed` | 2 single-sample spike(s), e.g. 14.9, 11.3 at 2016-06-06 05:00:00. | prepare() treats them as missing (by default). |

**Decisions recorded:**

- Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the dataset authors judged invalid are already removed, which shows up as missing).
- Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are available, so none is assumed).
- Buildings sampled at random among those with at least 90% of hours present, one per site in turn.

## Preparation

- mask_stuck `electricity`: 2 stuck stretch(es) set to missing. (155)
- mask_stuck `airTemperature`: 58 stuck stretch(es) set to missing. (149)
- mask_stuck `windSpeed`: 5 stuck stretch(es) set to missing. (12)
- mask_spikes `windSpeed`: Single-sample spikes set to missing. (2)
- resample: Resampled to a regular 1 h grid (17544 rows). (17544)
- forward_fill `airTemperature`: Filled input gaps up to 1h with the last known value. (62)
- forward_fill `dewTemperature`: Filled input gaps up to 1h with the last known value. (4)
- forward_fill `windSpeed`: Filled input gaps up to 1h with the last known value. (11)

## Split

| Set | From | To | Rows |
|---|---|---|---|
| train | 2016-01-01 00:00:00 | 2017-05-28 14:00:00 | 12169 |
| val | 2017-05-29 15:00:00 | 2017-09-14 05:00:00 | 2583 |
| test | 2017-09-15 06:00:00 | 2017-12-31 23:00:00 | 2585 |

Time-ordered, with a 1 d gap between sets.

## Validation

| model | type | RMSE | MAE | CV(RMSE) % | NMBE % | R² |
|---|---|---|---|---|---|---|
| gbm_change | ml | 12.853 | 9.204 | 6.561 | -0.892 | 0.828 |
| gbm | ml | 13.250 | 9.555 | 6.764 | -0.892 | 0.817 |
| ridge | ml | 14.057 | 10.171 | 7.176 | -1.143 | 0.794 |
| persistence | baseline | 14.809 | 9.595 | 7.559 | -0.132 | 0.772 |
| same_time_yesterday | baseline | 14.809 | 9.595 | 7.559 | -0.132 | 0.772 |
| same_time_last_week | baseline | 19.568 | 13.100 | 9.989 | -0.897 | 0.601 |
| towt | baseline | 38.871 | 32.267 | 19.842 | -6.237 | -0.574 |
| time_of_day_profile | baseline | 53.250 | 43.550 | 27.182 | -19.759 | -1.954 |
| time_of_week_profile | baseline | 53.265 | 43.554 | 27.190 | -19.769 | -1.955 |

## Test result

Chosen model: **gbm_change** {'base__min_samples_leaf': 20, 'base__max_leaf_nodes': 15, 'base__max_iter': 200, 'base__learning_rate': 0.05, 'base__l2_regularization': 0.1}

| Metric | Model | persistence |
|---|---|---|
| RMSE (kWh) | 20.774 | 20.227 |
| MAE (kWh) | 13.246 | 10.536 |
| CV(RMSE) % | 8.141 | 7.927 |
| NMBE % | 1.910 | 0.250 |
| R² | 0.931 | 0.935 |

Skill vs persistence: **-0.03** (1 = perfect, 0 = no better than the baseline).

ASHRAE Guideline 14 (hourly): CV(RMSE) 8.1% (limit 30%), NMBE 1.9% (limit ±10%): **passes**.

90% prediction interval: ±20.4 kWh (width from validation errors); it contained 78% of test values.

## Backtest (rolling origin)

The chosen model refitted before each block on all earlier data:

| Block | Rows | Skill |
|---|---|---|
| 2017-05-28 to 2017-08-09 | 1739 | 0.12 |
| 2017-08-09 to 2017-10-20 | 1739 | 0.13 |
| 2017-10-20 to 2017-12-31 | 1738 | -0.18 |

Pooled skill: **0.02**. The first blocks overlap the validation period used to choose the model; the single test period above is the untouched result.

## What the model relies on

Share of the model's accuracy lost when each input is scrambled (test period):

| Input | Share |
|---|---|
| electricity (recent history) | 90% |
| calendar (time of day, weekday) | 10% |

> Warning: The model is barely better than persistence on test data (skill -0.03).

## Plots

![timeseries](test_timeseries.png)
![scatter](test_scatter.png)
