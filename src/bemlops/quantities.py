"""Physical quantities found in building data.

Each quantity knows its canonical unit, how to convert other units into it,
and what values are physically plausible. The data checks use this table to
catch wrong units (a "degC" column that holds 68-75) and sensor faults
(a negative power reading), whatever the column happens to be called.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Tuple

import numpy as np

Converter = Callable[[np.ndarray], np.ndarray]

INF = float("inf")


def _identity(x):
    return x


def _scale(k: float) -> Converter:
    return lambda x: x * k


@dataclass(frozen=True)
class Quantity:
    """A measurable thing in a building, e.g. zone air temperature or CO2."""

    name: str
    canonical_unit: Optional[str]
    units: Dict[str, Converter]
    plausible: Tuple[float, float] = (-INF, INF)
    # Narrower "typical" range, used only to guess which unit the data is really in.
    typical: Optional[Tuple[float, float]] = None
    kind: str = "continuous"  # continuous | setpoint | binary | count | interval
    may_be_constant: bool = False  # setpoints, schedules: long flat runs are normal
    zero_runs_ok: bool = False  # solar at night, equipment off: long runs of 0 are normal
    spike_check: bool = True  # False where sharp jumps are real (on/off equipment)
    aggregate: str = "mean"  # how to resample: mean | sum | last
    headline_metric: str = "mae"  # "cvrmse" for energy-like targets, "mae" for IEQ
    brick: Optional[str] = None  # nearest Brick Schema class
    description: str = ""


# Units of temperature, converted to degC.
_TEMP = {
    "degC": _identity,
    "degF": lambda x: (x - 32.0) * 5.0 / 9.0,
    "K": lambda x: x - 273.15,
}
_PERCENT = {"%": _identity, "fraction": _scale(100.0)}
_POWER = {
    "kW": _identity,
    "W": _scale(1e-3),
    "MW": _scale(1e3),
    "Btu/h": _scale(2.9307107e-4),
    "MBH": _scale(0.29307107),  # thousand Btu/h
    "ton": _scale(3.5168525),  # refrigeration ton
    "hp": _scale(0.7456999),
}
_ENERGY = {
    "kWh": _identity,
    "Wh": _scale(1e-3),
    "MWh": _scale(1e3),
    "kBtu": _scale(0.29307107),
    "MMBtu": _scale(293.07107),
    "therm": _scale(29.307107),
    "ton-h": _scale(3.5168525),
}

QUANTITIES: Dict[str, Quantity] = {}


def _register(q: Quantity) -> None:
    QUANTITIES[q.name] = q


_register(Quantity("zone_air_temperature", "degC", _TEMP, plausible=(0, 50), typical=(10, 35),
                   brick="Zone_Air_Temperature_Sensor", description="Room or zone air temperature"))
_register(Quantity("outdoor_air_temperature", "degC", _TEMP, plausible=(-60, 60), typical=(-45, 52),
                   brick="Outside_Air_Temperature_Sensor", description="Outdoor dry-bulb temperature"))
_register(Quantity("supply_air_temperature", "degC", _TEMP, plausible=(-10, 80), typical=(5, 60),
                   spike_check=False, brick="Supply_Air_Temperature_Sensor",
                   description="Jumps are real when fans and coils cycle on and off"))
_register(Quantity("return_air_temperature", "degC", _TEMP, plausible=(0, 50), typical=(10, 35),
                   brick="Return_Air_Temperature_Sensor"))
_register(Quantity("mixed_air_temperature", "degC", _TEMP, plausible=(-40, 60), typical=(-20, 45),
                   brick="Mixed_Air_Temperature_Sensor"))
_register(Quantity("water_temperature", "degC", _TEMP, plausible=(-5, 110), typical=(1, 95),
                   brick="Water_Temperature_Sensor", description="Chilled, hot or condenser water"))
_register(Quantity("temperature_setpoint", "degC", _TEMP, plausible=(0, 50), typical=(10, 35),
                   kind="setpoint", may_be_constant=True, spike_check=False, aggregate="last",
                   brick="Temperature_Setpoint"))
_register(Quantity("relative_humidity", "%", _PERCENT, plausible=(0, 100), typical=(3, 100),
                   brick="Relative_Humidity_Sensor"))
_register(Quantity("co2", "ppm", {"ppm": _identity}, plausible=(250, 10000), typical=(300, 5000),
                   brick="CO2_Sensor", description="Carbon dioxide concentration"))
_register(Quantity("pm25", "ug/m3", {"ug/m3": _identity, "mg/m3": _scale(1e3)}, plausible=(0, 2000),
                   typical=(0, 500), zero_runs_ok=True, spike_check=False, brick="PM2.5_Sensor",
                   description="Short spikes are often real (cooking, cleaning, a passing truck)"))
_register(Quantity("illuminance", "lux", {"lux": _identity, "fc": _scale(10.7639)}, plausible=(0, 150000),
                   zero_runs_ok=True, spike_check=False, brick="Illuminance_Sensor",
                   description="Jumps are real (lights switching, sun patches)"))
_register(Quantity("electric_power", "kW", _POWER, plausible=(0, INF), zero_runs_ok=True, spike_check=False,
                   headline_metric="cvrmse", brick="Electric_Power_Sensor",
                   description="Electric demand; use net_electric_power for meters with on-site PV"))
_register(Quantity("net_electric_power", "kW", _POWER, zero_runs_ok=True, spike_check=False,
                   headline_metric="cvrmse", brick="Electric_Power_Sensor"))
_register(Quantity("thermal_power", "kW", _POWER, plausible=(0, INF), zero_runs_ok=True, spike_check=False,
                   headline_metric="cvrmse", brick="Thermal_Power_Sensor",
                   description="Cooling or heating rate (load)"))
_register(Quantity("energy", "kWh", _ENERGY, plausible=(0, INF), kind="interval", zero_runs_ok=True,
                   spike_check=False, aggregate="sum", headline_metric="cvrmse", brick="Energy_Sensor",
                   description="Energy used per interval (not a cumulative meter reading)"))
_register(Quantity("solar_irradiance", "W/m2", {"W/m2": _identity, "Btu/h-ft2": _scale(3.154591)},
                   plausible=(0, 1500), zero_runs_ok=True, spike_check=False, brick="Solar_Radiance_Sensor",
                   description="Jumps are real under broken clouds"))
_register(Quantity("wind_speed", "m/s", {"m/s": _identity, "mph": _scale(0.44704), "km/h": _scale(1 / 3.6)},
                   plausible=(0, 80), zero_runs_ok=True))
_register(Quantity("occupancy_count", "count", {"count": _identity}, plausible=(0, INF), kind="count",
                   zero_runs_ok=True, spike_check=False, brick="Occupancy_Count_Sensor"))
_register(Quantity("occupancy_status", "binary", {"binary": _identity}, plausible=(0, 1), kind="binary",
                   may_be_constant=True, zero_runs_ok=True, spike_check=False, brick="Occupancy_Status"))
_register(Quantity("equipment_status", "binary", {"binary": _identity}, plausible=(0, 1), kind="binary",
                   may_be_constant=True, zero_runs_ok=True, spike_check=False, brick="Status"))
_register(Quantity("position", "%", _PERCENT, plausible=(0, 100), may_be_constant=True, zero_runs_ok=True,
                   spike_check=False, brick="Position_Command",
                   description="Damper, valve or fan-speed position/command"))
_register(Quantity("airflow", "m3/s", {"m3/s": _identity, "cfm": _scale(4.719474e-4), "L/s": _scale(1e-3),
                                       "m3/h": _scale(1 / 3600)},
                   plausible=(0, INF), zero_runs_ok=True, spike_check=False, brick="Air_Flow_Sensor"))
_register(Quantity("pressure", "Pa", {"Pa": _identity, "kPa": _scale(1e3), "inH2O": _scale(249.0889),
                                      "psi": _scale(6894.757)},
                   brick="Pressure_Sensor"))
_register(Quantity("other", None, {}, may_be_constant=True, zero_runs_ok=True, spike_check=False,
                   description="Anything else, e.g. a feature you derived. No unit or range checks."))


# Common ways people (and BAS exports) write units.
_UNIT_ALIASES = {
    "c": "degC", "°c": "degC", "degc": "degC", "deg c": "degC", "celsius": "degC",
    "f": "degF", "°f": "degF", "degf": "degF", "deg f": "degF", "fahrenheit": "degF",
    "k": "K", "kelvin": "K",
    "%": "%", "%rh": "%", "percent": "%", "pct": "%", "fraction": "fraction", "0-1": "fraction",
    "ppm": "ppm",
    "ug/m3": "ug/m3", "µg/m3": "ug/m3", "μg/m3": "ug/m3", "mg/m3": "mg/m3",
    "lux": "lux", "lx": "lux", "fc": "fc", "footcandle": "fc",
    "kw": "kW", "w": "W", "mw": "MW", "btu/h": "Btu/h", "btuh": "Btu/h", "btu/hr": "Btu/h",
    "mbh": "MBH", "ton": "ton", "tons": "ton", "rt": "ton", "hp": "hp",
    "kwh": "kWh", "wh": "Wh", "mwh": "MWh", "kbtu": "kBtu", "mmbtu": "MMBtu", "therm": "therm",
    "therms": "therm", "ton-h": "ton-h", "ton-hr": "ton-h", "ton-hours": "ton-h",
    "w/m2": "W/m2", "w/m^2": "W/m2", "btu/h-ft2": "Btu/h-ft2",
    "m/s": "m/s", "mph": "mph", "km/h": "km/h",
    "count": "count", "people": "count", "persons": "count", "#": "count",
    "binary": "binary", "bool": "binary", "on/off": "binary", "0/1": "binary",
    "m3/s": "m3/s", "cfm": "cfm", "l/s": "L/s", "m3/h": "m3/h",
    "pa": "Pa", "kpa": "kPa", "inh2o": "inH2O", "in wc": "inH2O", "in. w.c.": "inH2O", "psi": "psi",
}


def normalize_unit(unit: Optional[str]) -> Optional[str]:
    """Map a unit string as written in the wild to the spelling used here."""
    if unit is None:
        return None
    u = unit.strip()
    if u == "":
        return None
    return _UNIT_ALIASES.get(u.lower(), u)


def get_quantity(name: str) -> Quantity:
    try:
        return QUANTITIES[name]
    except KeyError:
        known = ", ".join(sorted(QUANTITIES))
        raise ValueError(f"Unknown quantity '{name}'. Known quantities: {known}") from None


def to_canonical(values: np.ndarray, quantity: Quantity, unit: Optional[str]) -> np.ndarray:
    """Convert values from `unit` to the quantity's canonical unit."""
    if quantity.canonical_unit is None or unit is None:
        return values
    conv = quantity.units.get(unit)
    if conv is None:
        raise ValueError(
            f"Unit '{unit}' is not valid for {quantity.name}. Valid units: {sorted(quantity.units)}"
        )
    return conv(values)


def in_range_fraction(values: np.ndarray, bounds: Tuple[float, float]) -> float:
    v = values[np.isfinite(values)]
    if v.size == 0:
        return float("nan")
    lo, hi = bounds
    return float(np.mean((v >= lo) & (v <= hi)))


def guess_unit(values: np.ndarray, quantity: Quantity) -> Dict[str, float]:
    """For each candidate unit, the share of values that look plausible if read in that unit."""
    bounds = quantity.typical or quantity.plausible
    scores = {}
    for unit, conv in quantity.units.items():
        with np.errstate(all="ignore"):
            scores[unit] = in_range_fraction(conv(values), bounds)
    return scores
