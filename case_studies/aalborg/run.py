"""Aalborg case study: six office rooms and the building systems in Denmark, February-December 2023.

Data: Melgaard et al. (2024), Data in Brief 54, 110326; Zenodo doi:10.5281/zenodo.10673763 (CC BY 4.0).

Run:  python case_studies/download.py aalborg
      python case_studies/aalborg/run.py

Writes case_studies/aalborg/results/ (committed) and runs/aalborg/ (full run folders, local).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
import common  # noqa: E402

RAW = REPO / "data" / "raw" / "aalborg" / "dataset__2023_02_27__2023_12_31.csv"
OUT = HERE / "results"
RUNS = REPO / "runs" / "aalborg"
ROOMS = ["RoomA", "RoomB", "RoomC", "RoomD", "RoomE", "RoomF"]


# ----- Part 1: the agent's work (loading and declaring) -------------------------------
def load() -> pd.DataFrame:
    """Semicolon-separated, UTF-8 with BOM, '#N/A' for missing, an unnamed index column,
    timestamps like 2023-04-01T00:00:00+0200 whose offset switches at daylight saving."""
    df = pd.read_csv(RAW, sep=";", encoding="utf-8-sig", na_values=["#N/A"], low_memory=False)
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")])
    df = df[df["timestamp"].notna()]
    ts = pd.to_datetime(df.pop("timestamp"), format="%Y-%m-%dT%H:%M:%S%z", utc=True)
    df.index = pd.DatetimeIndex(ts).tz_convert("Europe/Copenhagen")
    return df


SOLAR = [f"Outdoor:Solar__direct_radiation__{side}_façade" for side in ("east", "south", "west")]
SYSTEM = {
    "Outdoor:Temperature_air": "outdoor_air_temperature [degC]",
    "Outdoor:Wind__velocity": "wind_speed [m/s]",
    **{c: {"quantity": "solar_irradiance", "unit": "W/m2", "flat_ok": True} for c in SOLAR},
    "Ventilation:EL_meter__power": "electric_power [W]",
    "Ventilation:Fan__air_flow__supply": "airflow [m3/h]",
    "Ventilation:Sensor__air_temperature__supply": "supply_air_temperature [degC]",
    "Heating:DH__power": "thermal_power [W]",
    "Ventilation:HC__power": "thermal_power [W]",
}


def room_columns(r: str) -> dict:
    return {
        f"{r}:Sensor__CO2": {"quantity": "co2", "unit": "ppm", "flat_ok": True},
        f"{r}:Sensor__room_temperature": "zone_air_temperature [degC]",
        f"{r}:People__amount": "occupancy_count",
        f"{r}:Room__active": "occupancy_status",
        f"{r}:Damper__position": "position [%]",
        f"{r}:Radiator__control_signal__motor_valve": "position [%]",
        f"{r}:Light__level__ceiling": "illuminance [lux]",
        f"{r}:Light__on_off_signal": "equipment_status",
        f"{r}:Window__opened_closed": "equipment_status",
        f"{r}:Control__setpoint_temperature_global": "temperature_setpoint [degC]",
        f"{r}:Control__heating_limit": "temperature_setpoint [degC]",
        f"{r}:Control__cooling_limit": "temperature_setpoint [degC]",
    }


NOTES = [
    "Timestamps carry UTC offsets that switch at daylight saving; converted to Europe/Copenhagen local time "
    "with the zone kept, so the repeated autumn hour and the missing spring hour are handled exactly.",
    "Units are not in the headers. Inferred from magnitudes and the dataset paper: district-heating, heating-coil "
    "and ventilation electric power in W, supply air flow in m3/h, temperatures in degC.",
    "Facade solar sensors never read exactly zero (night offset of 2-4 W/m2), so long flat night stretches are "
    "real: declared flat_ok.",
    "Heating:DH__energy_accumulated and Ventilation:EL_meter__energy_accumulated are cumulative meters; not used, "
    "since the matching power points carry the same information per interval.",
    "Room CO2 is logged on change of value: in Room A the reading is unchanged in 95% of 5-minute steps and "
    "moves by at least ~34 ppm when it changes (vs 9% unchanged for room temperature). Long flat stretches are "
    "therefore expected, not stuck sensors: CO2 declared flat_ok in every room.",
    "Outdoor temperature is NOT logged that way (34% unchanged, tiny steps), so its flat stretches (e.g. "
    "4.99997 degC for 37 h in November) are real faults and stay masked. Wind speed looks change-of-value "
    "logged too, but 25-hour holds are implausible, so it is left to masking (it is only an input).",
    "Room ventilation and heating are served by building systems that also serve other spaces; system points are "
    "inputs to room tasks, not room-level loads.",
]
PEOPLE_REASON = ("Camera people counts were only recorded for part of the year (documented by the dataset "
                 "authors). Missing targets are skipped, never filled; results cover the recorded periods.")

TASKS = []
for r in ROOMS:
    TASKS += [
        (r, f"{r}:Sensor__CO2", "1h", "Forecast room CO2 one hour ahead for demand-controlled ventilation."),
        (r, f"{r}:Sensor__room_temperature", "1h", "Forecast room temperature one hour ahead."),
        (r, f"{r}:People__amount", "1h", "Forecast the number of people in the room one hour ahead."),
        (r, f"{r}:Room__active", "1h", "Forecast whether the room will be in use one hour ahead (motion sensor)."),
    ]
TASKS += [
    (None, "Ventilation:EL_meter__power", "1h", "Forecast ventilation (AHU) electric power one hour ahead."),
    (None, "Heating:DH__power", "1h", "Forecast district-heating power one hour ahead."),
    (None, "Heating:DH__power", "24h", "Forecast district-heating power a day ahead (no weather forecast used)."),
]
PROTOCOL_ROOMS = {"RoomA", None}  # the evaluation-protocol comparison is run on these (it is costly)


# ----- Part 2: bemlops does the rest ------------------------------------------------------
def main() -> None:
    df = load()
    rows, protocol = [], []
    for room, target, horizon, use in TASKS:
        cols = dict(SYSTEM)
        if room:
            cols.update(room_columns(room))
        short = target.replace(":", "-").replace("__", "-").replace("_", "").lower()
        name = f"aalborg-{short}-{horizon}"
        accept = {f"missing:{target}": PEOPLE_REASON} if "People" in target else {}
        p, r, row = common.run_task(df, target, cols, horizon, name, RUNS, notes=NOTES, n_iter=3,
                                    intended_use=use, accept=accept)
        row.update({"dataset": "Aalborg", "building": room or "building systems"})
        rows.append(row)
        print(f"{name}: {row['status']} skill={row.get('skill')}", flush=True)
        if r is not None and p.task == "regression" and room in PROTOCOL_ROOMS:
            protocol.append(common.protocol_row("Aalborg", name, target, horizon, common.protocol_comparison(p)))
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "summary.csv", index=False)
    pd.DataFrame(protocol).to_csv(OUT / "protocol_comparison.csv", index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
