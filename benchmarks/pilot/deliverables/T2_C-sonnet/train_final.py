"""Fit the final model on all of train.csv and write model_artifacts.json (run once; predict() never retrains)."""
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model as m

df5 = m.clean5(m.load_raw(os.path.join(HERE, "train.csv")))
g = m.grid15(df5)
full = pd.date_range(g.index.min().floor("D"), g.index.max().floor("D") + pd.Timedelta("23h45min"), freq="15min")
g = g.reindex(full)
art = m.fit_artifacts(g)
art["trained_on"] = {"start": str(g.index.min()), "end": str(g["y"].dropna().index.max()),
                     "n_rows": art["n_train"], "note": "weekday on-window rows with valid chilled-water target"}
with open(m.ART_PATH, "w") as f:
    json.dump(art, f, indent=1)
print("saved", m.ART_PATH, "n_train", art["n_train"])
print("coef:", dict(zip(art["cols"], [round(c, 3) for c in art["coef"]])))
