"""A synthetic but realistic messy BAS export, for demos and tests.

One office zone (RM204) served by AHU1, simulated with a simple thermal and
CO2 model, then exported the way real BAS trend logs often look: cryptic
point names, Fahrenheit, text in number columns, -999 placeholders, a stuck
CO2 sensor, temperature spikes, dropped rows, an outage, duplicate and
out-of-order timestamps. Real case studies replace this with real buildings.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

# What the points actually are. Working this out is the agent's job; tests use it as ground truth.
OFFICE_POINTS = {
    "OAT": "outdoor_air_temperature [degF]",
    "SOL_RAD": "solar_irradiance [W/m2]",
    "RM204_ZN_T": "zone_air_temperature [degF]",
    "RM204_ZN_SP": "temperature_setpoint [degF]",
    "RM204_CO2": "co2 [ppm]",
    "RM204_OCC": "occupancy_count [count]",
    "AHU1_CLG_KW": "electric_power [kW]",
}


def _ar1(rng: np.random.Generator, n: int, phi: float, sigma: float) -> np.ndarray:
    out = np.zeros(n)
    e = rng.normal(0, sigma, n)
    for i in range(1, n):
        out[i] = phi * out[i - 1] + e[i]
    return out


def simulate_office(days: int = 60, seed: int = 0, start: str = "2025-09-15") -> pd.DataFrame:
    """Clean 5-minute simulation in SI units (the 'truth' before export problems)."""
    rng = np.random.default_rng(seed)
    dt = 300.0
    idx = pd.date_range(start, periods=days * 288, freq="5min")
    n = len(idx)
    hour = np.asarray(idx.hour + idx.minute / 60.0)
    dow = np.asarray(idx.day_of_week)
    day = np.arange(n) // 288
    t_days = np.arange(n) * dt / 86400.0

    oat = (31 - 11 * t_days / days + 7.5 * np.cos(2 * np.pi * (hour - 15) / 24)
           + rng.normal(0, 1.5, days + 1)[day] + _ar1(rng, n, 0.995, 0.05))
    sun = np.clip(np.sin(np.pi * (hour - 6.5) / 12.5), 0, None) ** 1.3
    solar = 950 * sun * rng.uniform(0.35, 1.0, days + 1)[day] * (1 - 0.15 * t_days / days)

    workday = dow < 5
    office_hours = workday & (hour >= 8) & (hour < 17.5)
    lunch = (hour >= 12) & (hour < 13)
    occ = rng.poisson(np.where(office_hours, 9 * np.where(lunch, 0.65, 1.0), 0.0)).astype(float)
    occupied_mode = workday & (hour >= 7) & (hour < 19)
    setpoint = np.where(occupied_mode, 23.3, 26.7)
    internal = 110 * occ + np.where(office_hours, 900, 250)

    C, UA, aperture, q_max, kp = 2.5e6, 180.0, 3.5, 9000.0, 4000.0
    tz = np.empty(n)
    q = np.empty(n)
    tz[0] = 25.0
    for i in range(n):
        q[i] = np.clip(kp * (tz[i] - setpoint[i] + 0.3), 0, q_max)
        if i + 1 < n:
            gain = UA * (oat[i] - tz[i]) + aperture * solar[i] + internal[i] - q[i]
            tz[i + 1] = tz[i] + dt / C * gain + rng.normal(0, 0.01)
    cop = np.clip(3.8 - 0.05 * (oat - 25), 2.2, 5.0)
    fan = np.where(occupied_mode | (q > 0), 0.6, 0.0)
    kw = np.clip(q / cop / 1000 + fan + rng.normal(0, 0.03, n), 0, None)

    V = 200.0
    qv = np.where(occupied_mode, 0.12, 0.015)
    co2 = np.empty(n)
    co2[0] = 450.0
    for i in range(n - 1):
        co2[i + 1] = co2[i] + dt / V * (5.2 * occ[i] - qv[i] * (co2[i] - 420.0))
    co2 = co2 + rng.normal(0, 8, n)

    return pd.DataFrame({"oat_c": oat, "solar_wm2": solar, "zone_t_c": tz, "setpoint_c": setpoint,
                         "co2_ppm": co2, "occupants": occ, "cooling_kw": kw}, index=idx)


def messy_office(days: int = 60, seed: int = 0, start: str = "2025-09-15") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """The simulation exported as a messy BAS trend log.

    Returns (export, truth): `export` has a text 'Timestamp' column like a real
    CSV export; `truth` lists the problems that were planted, for tests.
    """
    rng = np.random.default_rng(seed + 1)
    sim = simulate_office(days, seed, start)
    f = lambda c: c * 9 / 5 + 32  # noqa: E731
    out = pd.DataFrame(index=sim.index)
    out["OAT"] = f(sim["oat_c"]).round(1).astype(object)
    out["SOL_RAD"] = sim["solar_wm2"].round(1)
    out["RM204_ZN_T"] = f(sim["zone_t_c"]).round(1)
    out["RM204_ZN_SP"] = f(sim["setpoint_c"]).round(1)
    out["RM204_CO2"] = sim["co2_ppm"].round(0).astype(object)
    out["RM204_OCC"] = sim["occupants"].astype(int)
    out["AHU1_CLG_KW"] = sim["cooling_kw"].round(2)
    out["AHU1_ALARM"] = np.where(rng.random(len(out)) < 0.01, "Alarm", "Normal")
    n = len(out)
    truth: Dict[str, Any] = {"points": dict(OFFICE_POINTS)}

    # Some outdoor temperatures exported with the unit inside the text.
    pos = rng.choice(n, 30, replace=False)
    out.iloc[pos, out.columns.get_loc("OAT")] = [f"{v} °F" for v in out["OAT"].iloc[pos]]
    truth["oat_text_numbers"] = 30

    # CO2 sensor freezes for 5 days, and reports OFFLINE now and then.
    i0, i1 = 38 * 288 + 100, 43 * 288 + 100
    frozen = out["RM204_CO2"].iloc[i0]
    out.iloc[i0:i1, out.columns.get_loc("RM204_CO2")] = frozen
    truth["co2_stuck"] = (out.index[i0], out.index[i1 - 1])
    pos = rng.choice(np.r_[0:i0, i1:n], 25, replace=False)
    out.iloc[pos, out.columns.get_loc("RM204_CO2")] = "OFFLINE"
    truth["co2_offline"] = 25

    # The power meter writes -999 when a reading is missing.
    pos = rng.choice(n, 20, replace=False)
    out.iloc[pos, out.columns.get_loc("AHU1_CLG_KW")] = -999.0
    truth["kw_sentinels"] = 20

    # Electrical noise: a few single-sample zone temperature spikes.
    pos = rng.choice(np.arange(10, n - 10), 8, replace=False)
    out.iloc[pos, out.columns.get_loc("RM204_ZN_T")] = out["RM204_ZN_T"].iloc[pos] + 25.0
    truth["zone_spikes"] = 8

    # A 7-hour controller outage, plus randomly dropped rows.
    o0 = out.index[22 * 288 + 12]
    o1 = o0 + pd.Timedelta(hours=7)
    keep = ~((out.index >= o0) & (out.index < o1))
    keep &= rng.random(n) > 0.025
    out = out[keep]
    truth["outage"] = (o0, o1)

    # An hour of rows exported twice, and a block written out of order.
    d0 = out.index.searchsorted(out.index[0] + pd.Timedelta(days=30, hours=1))
    dup = out.iloc[d0:d0 + 12].copy()
    out = pd.concat([out.iloc[:d0 + 12], dup, out.iloc[d0 + 12:]])
    truth["duplicates"] = 12
    b0 = len(out) // 2
    block = out.iloc[b0:b0 + 20].iloc[::-1]
    out = pd.concat([out.iloc[:b0], block, out.iloc[b0 + 20:]])

    export = out.reset_index(names="Timestamp")
    export["Timestamp"] = export["Timestamp"].dt.strftime("%m/%d/%Y %I:%M:%S %p")
    return export, truth
