import sys, os, tempfile, importlib.util
import numpy as np, pandas as pd
spec = importlib.util.spec_from_file_location("mdl", "model.py"); mdl = importlib.util.module_from_spec(spec); spec.loader.exec_module(mdl)
raw = pd.read_csv("train.csv")
tmp = tempfile.mkdtemp()
def run(name, df):
    f = os.path.join(tmp, name + ".csv"); df.to_csv(f, index=False)
    try:
        p = mdl.predict(f)
        print(f"{name:28s} OK n={len(p)} nan={int(p.isna().sum())} min={p.min():.2f} max={p.max():.2f} idx_ok={p.index.is_monotonic_increasing and not p.index.has_duplicates}")
    except Exception as e:
        print(f"{name:28s} FAIL {type(e).__name__}: {e}")
ts = pd.to_datetime(raw.timestamp.str.replace(" +08:00", ""), format="%Y-%m-%d %H:%M")
# weekend dates: shift all days by +4 days (Tue->Sat)
d = raw.copy(); d["timestamp"] = (ts + pd.Timedelta(days=4)).dt.strftime("%Y-%m-%d %H:%M") + " +08:00"; run("shifted_to_weekend", d)
d = raw.drop(columns=[c for c in raw.columns if c.startswith("dry_bulb") or c.startswith("occupant")]); run("missing_cols", d)
d = raw.iloc[:50].copy(); run("tiny_50rows", d)
d = raw.iloc[:1].copy(); run("one_row", d)
d = raw.iloc[::-1].copy(); run("reversed_rows", d)
d = raw.copy(); d["timestamp"] = d.timestamp.str.replace("+08:00", "+07:00"); run("other_offset", d)
d = raw.copy(); d["dry_bulb_temp [Celsius]"] = d["dry_bulb_temp [Celsius]"] * 1.8 + 32; d["offcoil_air_temp [Celsius]"] = d["offcoil_air_temp [Celsius]"] * 1.8 + 32; run("exog_in_degF", d)
d = raw.copy(); d["chilled_water_energy [kWh]"] = -999; run("target_all_-999", d)
d = raw.copy(); d["chilled_water_energy [kWh]"] = np.nan; d["cooling_coil_valve_command [%]"] = np.nan; run("target_all_nan", d)
d = raw.iloc[-300:].copy(); run("last_300_rows", d)
