import json, sys

usability = sys.argv[1] if len(sys.argv) > 1 else ""
rep = {
    "expected_rmse": 35.0,
    "evaluation": (
        "Rolling-origin (expanding window) evaluation on train.csv, refitting the full pipeline on all earlier data each time "
        "(training targets end before the test block, 1 h gap, so no label leakage): 3 blocks 27 Mar-17 Apr, 17 Apr-8 May, 8 May-1 Jun gave "
        "RMSE 44.8 / 40.3 / 26.5 ppm (pooled 37.5) vs persistence of the 1 h-old value 46.4 / 48.0 / 28.5 (pooled 41.3), i.e. about 9% better; "
        "~8 model/feature variants were compared on the same blocks so the pooled figure is slightly optimistic, and error scales with how much "
        "weekday occupancy there is (blocks range 26-45 ppm), so I quote 35 ppm with a plausible range of 25-45; a quiet summer/holiday period "
        "would give much less (about 10-20 ppm). predict() was also checked mechanically: truncating the file, and overwriting all data after a "
        "time T0 with random rows, leaves forecasts for every interval <= T0+45 min bit-for-bit unchanged. bemlops' own fit() on its last-15% test window "
        "(late May) reported persistence 29.5 ppm and no ML model beating it."
    ),
    "data_findings": (
        "Raw 5-min export, 27,204 rows, 2023-02-27 to 2023-05-31, 22 columns, ';' separator, UTF-8 BOM, '#N/A' for missing, timestamps with UTC offsets "
        "(+0100 -> +0200 at the 2023-03-26 DST change). "
        "(1) Row order/duplicates: a 288-row block (2023-05-24 23:05 to 2023-05-25 23:00) is logged twice (identical values); a 30-row block on 2023-04-24 "
        "(15:30 back to 13:05) is in reverse order and actually fills a 2.5 h hole; a 12 h gap on 2023-04-02 (07:40-19:45); the DST jump. Fixed by parsing to UTC, sorting, "
        "dropping exact duplicate timestamps, then working on a UTC grid and converting to local time only for calendar features and the output index. "
        "(2) RoomB CO2: 15 placeholders of -999 (masked), one isolated needle of 1521 ppm on 2023-04-21 (kept out of the inputs via a bin-median feature; cannot be predicted), "
        "and the point is change-of-value logged (95% of consecutive samples identical, steps of ~50 ppm, flat for up to 3.6 days when the room is empty), so long flat "
        "stretches are real and not a stuck sensor: they were NOT masked. The target is the mean of such held values, which makes it step-like and hard to forecast; "
        "the persistence baseline is therefore strong. "
        "(3) Room temperature changed unit from degC to degF at 2023-05-12 10:00 (values 70-83 until the end of the file): converted per sample (>45 means degF). "
        "(4) Outdoor temperature has 8 isolated spikes to 57-73 (glitches): masked (>35). Wind has 12 'OFFLINE' text values (-> NaN). "
        "(5) People__amount is only logged for 38% of the time (27 Feb-13 Apr and 30-31 May, flat 0 in between/NaN elsewhere), so it was NOT used (it would be missing in the future). "
        "The three setpoint/limit columns are constant and were dropped. Window open/closed changes only three times (8 May, 17 May, 23 May) so it is confounded with the period and was left out. "
        "(6) Regime change around 14-24 Apr: ventilation/damper behaviour and the Room__active pattern changed (weekday office-hour block afterwards, ad hoc bursts before), "
        "so training data is from two regimes. "
        "(7) Errors are concentrated on weekday afternoons (16-19 h) with sudden event-driven rises of 300-400 ppm within an hour that no 1 h-old information predicts; "
        "nights and weekends are easy (RMSE 10-20 ppm). "
        "Model inputs: bin means/median/last/min/max of the 15-min CO2, rolling CO2 stats, room occupancy flag (Room__active) and its history, ventilation airflow, damper, lights on/off, "
        "local time of day/weekday and the occupancy pattern of the previous 1-7 days at the same time. Outdoor temperature, solar, heating power, room temperature level and light level were "
        "excluded on purpose because with only 3 months of data they mostly encode 'season' and would extrapolate badly into summer. "
        "All lagged inputs are at least 4 bins (1 h) old; the target mean for interval T only uses 5-min samples with timestamps before T-45 min. "
        "predict() returns forecasts from the first interval in the file up to 1 h after the last complete 15-min bin (the live forecast); where no CO2 history exists "
        "(first hour of the file, long gaps) it falls back to the weekday/hour median from training."
    ),
    "usability": usability,
}
json.dump(rep, open("report.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("report.json written")
