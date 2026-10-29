"""Quickstart: from a messy BAS export to a checked, deployable forecast.

Run:  python examples/quickstart.py

This mimics what an AI agent (or an engineer) does with the package:
  part 1 - look at the export and declare what the points mean (judgment)
  part 2 - let bemlops check, prepare, fit and record (guardrails)
The same code then forecasts a different target (zone CO2), which is the point:
one workflow for any prediction task in a building.
"""

from pathlib import Path

import pandas as pd

import bemlops
from bemlops.datasets import messy_office

RUNS = Path(__file__).resolve().parent.parent / "runs"

# Part 1: the export, and what the agent works out about it ------------------
export, _ = messy_office(days=60, seed=0)
print(export.head(), "\n")
print(export.dtypes, "\n")

# The agent decodes the point names. It gets one wrong on purpose here:
# RM204_ZN_T is declared in degC, but the BAS actually trends it in degF.
columns = {
    "AHU1_CLG_KW": "electric_power [kW]",
    "OAT": "outdoor_air_temperature [degF]",
    "SOL_RAD": "solar_irradiance [W/m2]",
    "RM204_ZN_T": "zone_air_temperature [degC]",  # mistake
    "RM204_ZN_SP": "temperature_setpoint [degF]",
    "RM204_CO2": "co2 [ppm]",
    "RM204_OCC": "occupancy_count",
}

# Part 2: bemlops checks the agent's work -------------------------------------
p = bemlops.Project(export, target="AHU1_CLG_KW", columns=columns, horizon="1h",
                    timestamp="Timestamp", timestamp_format="%m/%d/%Y %I:%M:%S %p",
                    name="ahu1-cooling-power-1h")
print(p.check_data(), "\n")

try:
    p.fit()
except bemlops.UnresolvedIssues as blocked:
    print("fit() refused:\n", blocked, "\n")

# The agent reads the error, checks the BAS point configuration, and fixes the declaration.
p.update(columns={"RM204_ZN_T": "zone_air_temperature [degF]"},
         note="RM204_ZN_T is trended in degF per the BAS point configuration.")
p.note("AHU1_ALARM left undeclared: alarm flag, not a physical input.")

p.prepare(freq="15min")
results = p.fit(n_iter=6)
print(results, "\n")
folder = p.save_run(RUNS)
print(f"Run saved to {folder}\n")

# Deployment: forecast from the latest data, then check for drift -------------
model = bemlops.load_model(folder / "model.joblib")
raw = p.raw  # in operation this would be the latest trend-log pull
end = raw.index.max()
forecast = model.predict(raw.loc[raw.index >= end - pd.Timedelta(days=10)])
print("Live forecast (next hour):")
print(forecast.tail(model.horizon)[["predicted", "forecast_made_at"]], "\n")
print("Drift check on the last two weeks:", model.check_drift(raw.loc[raw.index >= end - pd.Timedelta(days=14)]))

# Same workflow, different target: zone CO2, 30 minutes ahead -----------------
q = bemlops.Project(export, target="RM204_CO2", horizon="30min", timestamp="Timestamp",
                    timestamp_format="%m/%d/%Y %I:%M:%S %p", name="rm204-co2-30min",
                    columns={**columns, "RM204_ZN_T": "zone_air_temperature [degF]"})
q.check_data()
q.prepare(freq="15min")
print(q.fit(n_iter=6))
q.save_run(RUNS)
