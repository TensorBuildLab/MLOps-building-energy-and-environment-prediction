"""BDG2 case study: the same day-ahead electricity task, fully automated, on a sample of real buildings.

Data: Miller et al. (2020), The Building Data Genome Project 2, Scientific Data 7, 368
(GitHub buds-lab/building-data-genome-project-2; treated as CC BY-SA 4.0, nothing redistributed).

One configuration, decided once by the agent for the whole dataset, is applied to every sampled
building: hourly electricity (kWh) forecast 24 h ahead from past load, past weather (no weather
forecast) and calendar. The question is how far one checked configuration scales.

Run:  python case_studies/download.py bdg2
      python case_studies/bdg2/run.py [n_buildings]
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
import common  # noqa: E402

RAW = REPO / "data" / "raw" / "bdg2"
OUT = HERE / "results"
RUNS = REPO / "runs" / "v3" / "bdg2"

NOTES = [
    "Electricity is hourly kWh per interval in naive local time per site (BDG2 cleaned meters; values the "
    "dataset authors judged invalid are already removed, which shows up as missing).",
    "Weather is the site's station data; it is used only up to the forecast time (no weather forecasts are "
    "available, so none is assumed).",
    "Buildings sampled at random among those with at least 90% of hours present, one per site in turn.",
]
COLUMNS = {
    "electricity": "energy [kWh]",
    "airTemperature": "outdoor_air_temperature [degC]",
    "dewTemperature": {"quantity": "other", "description": "dew point, degC"},
    "windSpeed": "wind_speed [m/s]",
}


def sample(n: int = 200, seed: int = 0) -> pd.DataFrame:
    """The pre-specified sample (ANALYSIS_PLAN_v3.md): buildings with >= 90% of hours present in the cleaned
    meters, at sites with weather; shuffled with `seed`, then taken round-robin over sites; the first n."""
    md = pd.read_csv(RAW / "metadata.csv")
    elec = pd.read_csv(RAW / "electricity_cleaned.csv", parse_dates=["timestamp"], index_col="timestamp")
    weather = pd.read_csv(RAW / "weather.csv", parse_dates=["timestamp"])
    coverage = elec.notna().mean()
    eligible = md[md["building_id"].isin(coverage[coverage >= 0.9].index)]
    eligible = eligible[eligible["site_id"].isin(weather["site_id"].unique())]
    shuffled = eligible.sample(frac=1.0, random_state=seed)
    shuffled["rank"] = shuffled.groupby("site_id").cumcount()
    picks = shuffled.sort_values(["rank", "site_id"]).head(n).copy()
    picks["order"] = range(len(picks))
    picks["coverage"] = picks["building_id"].map(coverage)
    return picks, elec, weather, len(eligible)


def building_frame(bid: str, site: str, elec: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    w = (weather[weather["site_id"] == site].set_index("timestamp")[["airTemperature", "dewTemperature",
                                                                      "windSpeed"]].reindex(elec.index))
    return pd.concat([elec[bid].rename("electricity"), w], axis=1)


def main(n: int = 200, seed: int = 0, part: int = 0, parts: int = 1) -> None:
    picks, elec, weather, n_eligible = sample(n, seed)
    print(f"{n_eligible} eligible buildings; sampled {len(picks)} from {picks['site_id'].nunique()} sites", flush=True)

    rows = []
    for _, b in picks.iterrows():
        if int(b["order"]) % parts != part:
            continue
        bid, site = b["building_id"], b["site_id"]
        df = building_frame(bid, site, elec, weather)
        t0 = time.time()
        p, r, row = common.run_task(df, "electricity", COLUMNS, "24h", f"bdg2-{bid}", RUNS, notes=NOTES,
                                    freq="1h", n_iter=3, models=("ridge", "gbm", "gbm_change"),
                                    intended_use="Day-ahead hourly electricity forecast for operations planning.")
        row.update({"dataset": "BDG2", "building": bid, "site": site, "primary_use": b["primaryspaceusage"],
                    "sqm": b["sqm"], "coverage": float(b["coverage"]), "order": int(b["order"]),
                    "seconds": round(time.time() - t0, 1)})
        rows.append(row)
        print(f"{bid}: {row['status']} skill={row.get('skill')} g14={row.get('g14_pass')} "
              f"({row['seconds']} s)", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    suffix = "" if parts == 1 else f"_part{part}"
    pd.DataFrame(rows).to_csv(OUT / f"summary{suffix}.csv", index=False)
    print(f"Wrote {OUT}")


def merge() -> None:
    parts = sorted(OUT.glob("summary_part*.csv"))
    df = pd.concat([pd.read_csv(f) for f in parts], ignore_index=True).sort_values("order")
    df.to_csv(OUT / "summary.csv", index=False)
    for f in parts:
        f.unlink()
    print(f"Merged {len(parts)} parts in {OUT}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "merge":
        merge()
    elif len(sys.argv) > 1:
        i, k = map(int, sys.argv[1].split("/"))
        main(200, 0, i, k)
    else:
        main()
