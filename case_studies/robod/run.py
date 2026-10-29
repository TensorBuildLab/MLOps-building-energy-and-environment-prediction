"""ROBOD case study: five rooms of a university building in Singapore, nine prediction targets per room.

Data: Tekler et al. (2022), ROBOD, room-level occupancy and building operation dataset,
Building Simulation 15, 2127-2137; figshare doi:10.6084/m9.figshare.19234530 (CC BY 4.0).

Run:  python case_studies/download.py robod
      python case_studies/robod/run.py

Writes case_studies/robod/results/ (summary tables, committed) and runs/robod/ (full run folders, local).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
import common  # noqa: E402

RAW = REPO / "data" / "raw" / "robod"
OUT = HERE / "results"
RUNS = REPO / "runs" / "robod"

ROOMS = {1: "lecture room", 2: "lecture room", 3: "office", 4: "research office", 5: "library"}


# ----- Part 1: the agent's work (loading and declaring) -------------------------------
def load(room: int) -> pd.DataFrame:
    """Headers look like 'indoor_co2 [ppm]'; timestamps like '2021-09-07 00:00 +08:00'."""
    df = pd.read_csv(RAW / f"combined_Room{room}.csv")
    ts = pd.to_datetime(df.pop("timestamp"), format="%Y-%m-%d %H:%M %z")
    df.index = pd.DatetimeIndex(ts).tz_convert("Asia/Singapore")  # keep local time; Singapore has no DST
    df.columns = [c.split(" [")[0] for c in df.columns]
    return df


# What each column is, worked out from the headers, the dataset paper and the value ranges.
COLUMNS = {
    "indoor_co2": {"quantity": "co2", "unit": "ppm", "flat_ok": True},
    "air_temperature": "zone_air_temperature [degC]",
    "indoor_relative_humidity": "relative_humidity [%]",
    "pm2.5": "pm25 [ug/m3]",
    "illuminance": "illuminance [lux]",
    "voc": "other",
    "sound_pressure_level": "other",
    "wifi_connected_devices": "other",
    "occupant_count": "occupancy_count",
    "occupant_presence": "occupancy_status",
    "plug_load_energy": "energy [kWh]",
    "lighting_energy": "energy [kWh]",
    "chilled_water_energy": "energy [kWh]",
    "temp_setpoint": "temperature_setpoint [degC]",
    "supply_air_temperature": "supply_air_temperature [degC]",
    "damper_position": "position [%]",
    "supply_air_flow": "airflow [m3/h]",
    "dry_bulb_temp": "outdoor_air_temperature [degC]",
    "global_horizontal_solar_radiation": "solar_irradiance [W/m2]",
    "outdoor_relative_humidity": {"quantity": "relative_humidity", "unit": "%", "flat_ok": True},
}

NOTES = [
    "Timestamps carry +08:00; converted to Asia/Singapore local time (no daylight saving).",
    "indoor_co2 never reads below exactly 400 ppm: a sensor floor, so long flat stretches at 400 in an "
    "empty room are real. Declared flat_ok so they are not masked as a stuck sensor.",
    "wifi_connected_devices declared 'other': a proxy for occupancy, not a count of people.",
    "Energy columns are kWh per 5-minute interval (not cumulative), so declared as interval energy.",
    "ahu_fan_energy not used: identical statistics in Rooms 4 and 5 suggest a shared AHU, not room-level data.",
    "Data cover weekdays in separate blocks between September and December 2021; gaps between blocks stay missing.",
    "outdoor_relative_humidity sits at 99.9-100% for many hours on tropical nights: saturation, not a stuck "
    "sensor. Declared flat_ok.",
]

TASKS = [
    ("indoor_co2", "30min", (), "Forecast CO2 30 min ahead to pre-ventilate."),
    ("air_temperature", "30min", (), "Forecast room temperature 30 min ahead."),
    ("indoor_relative_humidity", "30min", (), "Forecast humidity 30 min ahead (tropical climate)."),
    ("pm2.5", "30min", (), "Forecast PM2.5 30 min ahead."),
    ("occupant_count", "30min", (), "Forecast the number of people 30 min ahead."),
    ("occupant_presence", "30min", (), "Forecast whether the room is occupied 30 min ahead."),
    ("occupant_count", 0, ("occupant_presence",),
     "Estimate the number of people now from Wi-Fi, CO2, sound and plug loads (virtual people counter)."),
    ("chilled_water_energy", "1h", (), "Forecast chilled-water energy one hour ahead."),
    ("plug_load_energy", "1h", (), "Forecast plug-load energy one hour ahead."),
]


# ----- Part 2: bemlops does the rest ------------------------------------------------------
def main() -> None:
    rows, protocol = [], []
    for room, kind in ROOMS.items():
        df = load(room)
        for target, horizon, drop, use in TASKS:
            mode = "now" if horizon == 0 else horizon
            name = f"robod-room{room}-{target.replace('.', '')}-{mode}"
            notes = NOTES + ([f"{', '.join(drop)} excluded: it comes from the same camera ground truth as the "
                              f"target, so it would leak the answer."] if drop else [])
            p, r, row = common.run_task(df, target, COLUMNS, horizon, name, RUNS, notes=notes, drop=drop,
                                        intended_use=use)
            row.update({"dataset": "ROBOD", "building": f"Room {room} ({kind})"})
            rows.append(row)
            print(f"{name}: {row['status']} skill={row.get('skill')}", flush=True)
            if r is not None and p.task == "regression":
                comp = common.protocol_comparison(p)
                protocol.append(common.protocol_row("ROBOD", name, target, horizon, comp))
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "summary.csv", index=False)
    pd.DataFrame(protocol).to_csv(OUT / "protocol_comparison.csv", index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
