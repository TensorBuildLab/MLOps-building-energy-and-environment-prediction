"""Column declarations: what each column means and what unit it is in.

Real BAS exports use names like ``RM204_ZN_T`` or ``AI-3.PV``. Working out what
they mean is the AI agent's (or engineer's) job. Writing that down here is
required: only declared columns are used, and every declaration is checked
against the data.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Optional, Union

from .quantities import QUANTITIES, Quantity, get_quantity, normalize_unit


@dataclass
class ColumnSpec:
    """What one column means.

    known_ahead: True when the value at the prediction time is available in
    advance (a weather forecast, an occupancy schedule, a planned setpoint).
    Leave False for measured values: then only past values are used, which is
    what keeps forecasts honest.

    flat_ok: True when long flat stretches are normal for this particular sensor,
    e.g. a CO2 sensor that reports a floor of exactly 400 ppm in an empty room.
    Turns off the stuck-sensor check and masking for this column only. A judgment
    call: record why with Project.note().
    """

    name: str
    quantity: str = "other"
    unit: Optional[str] = None
    known_ahead: bool = False
    description: str = ""
    flat_ok: bool = False

    def __post_init__(self) -> None:
        self.quantity = resolve_quantity_name(self.quantity)
        self.unit = normalize_unit(self.unit)
        q = self.q
        if self.unit is None and q.canonical_unit is not None and len(q.units) == 1:
            self.unit = q.canonical_unit  # e.g. ppm, count: only one choice

    @property
    def q(self) -> Quantity:
        return get_quantity(self.quantity)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Everyday names for quantities, so a declaration like "zone temp [degF]" works.
_QUANTITY_ALIASES = {
    "zone_temperature": "zone_air_temperature",
    "zone_temp": "zone_air_temperature",
    "room_temperature": "zone_air_temperature",
    "room_temp": "zone_air_temperature",
    "indoor_temperature": "zone_air_temperature",
    "indoor_air_temperature": "zone_air_temperature",
    "space_temperature": "zone_air_temperature",
    "outdoor_temperature": "outdoor_air_temperature",
    "outside_air_temperature": "outdoor_air_temperature",
    "oat": "outdoor_air_temperature",
    "dry_bulb": "outdoor_air_temperature",
    "supply_air_temp": "supply_air_temperature",
    "discharge_air_temperature": "supply_air_temperature",
    "sat": "supply_air_temperature",
    "setpoint": "temperature_setpoint",
    "zone_setpoint": "temperature_setpoint",
    "humidity": "relative_humidity",
    "rh": "relative_humidity",
    "carbon_dioxide": "co2",
    "pm2.5": "pm25",
    "pm_2.5": "pm25",
    "power": "electric_power",
    "electric_demand": "electric_power",
    "electricity_demand": "electric_power",
    "demand": "electric_power",
    "cooling_rate": "thermal_power",
    "cooling_load": "thermal_power",
    "heating_rate": "thermal_power",
    "heating_load": "thermal_power",
    "electricity": "energy",
    "electric_energy": "energy",
    "consumption": "energy",
    "solar_radiation": "solar_irradiance",
    "irradiance": "solar_irradiance",
    "ghi": "solar_irradiance",
    "occupancy": "occupancy_count",
    "occupants": "occupancy_count",
    "people_count": "occupancy_count",
    "occupied": "occupancy_status",
    "status": "equipment_status",
    "on_off": "equipment_status",
    "damper_position": "position",
    "valve_position": "position",
    "fan_speed": "position",
    "flow": "airflow",
    "air_flow": "airflow",
}


def resolve_quantity_name(name: str) -> str:
    key = re.sub(r"[\s\-]+", "_", name.strip().lower())
    if key in QUANTITIES:
        return key
    if key in _QUANTITY_ALIASES:
        return _QUANTITY_ALIASES[key]
    get_quantity(key)  # raises a helpful error listing valid names
    return key


_SHORTHAND = re.compile(r"^\s*(?P<q>[^\[,(]+?)\s*(?:[\[,(]\s*(?P<u>[^\]\)]*?)\s*[\])]?)?\s*$")


def parse_spec(name: str, value: Union[str, Mapping[str, Any], ColumnSpec]) -> ColumnSpec:
    """Accept a ColumnSpec, a dict, or a shorthand string.

    Shorthand examples: ``"zone_air_temperature [degF]"``,
    ``"co2"``, ``"cooling load, kW"``.
    """
    if isinstance(value, ColumnSpec):
        if value.name != name:
            value = ColumnSpec(name, value.quantity, value.unit, value.known_ahead, value.description,
                               value.flat_ok)
        return value
    if isinstance(value, Mapping):
        return ColumnSpec(name=name, **dict(value))
    if isinstance(value, str):
        m = _SHORTHAND.match(value)
        if not m:
            raise ValueError(f"Cannot read the declaration for '{name}': {value!r}")
        unit = m.group("u")
        return ColumnSpec(name=name, quantity=m.group("q"), unit=unit if unit else None)
    raise TypeError(f"Declaration for '{name}' must be a string, dict or ColumnSpec, got {type(value)!r}")


def parse_columns(columns: Mapping[str, Union[str, Mapping[str, Any], ColumnSpec]]) -> Dict[str, ColumnSpec]:
    return {name: parse_spec(name, value) for name, value in columns.items()}


def to_time_index(data, timestamp: Optional[str] = None, timestamp_format: Optional[str] = None):
    """Return a copy of `data` indexed by time, plus a note on anything worth logging.

    Used identically in training and in deployment, so live data is read the same way.
    """
    import warnings

    import pandas as pd

    df = data.copy()
    note = ""
    if timestamp is not None and timestamp in df.columns:
        if timestamp_format:
            ts = pd.to_datetime(df[timestamp], format=timestamp_format, errors="coerce")
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                ts = pd.to_datetime(df[timestamp], errors="coerce")
            note = "Timestamp format was guessed; pass timestamp_format to be sure. "
        bad = int(ts.isna().sum())
        df = df.drop(columns=[timestamp])
        df.index = pd.DatetimeIndex(ts)
        if bad:
            df = df[df.index.notna()]
            note += f"{bad} rows had unreadable timestamps and were dropped."
    elif not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except (ValueError, TypeError) as exc:
            raise ValueError("The data needs a time index. Pass timestamp='<time column>' "
                             "or set a DatetimeIndex first.") from exc
    return df, note.strip()
