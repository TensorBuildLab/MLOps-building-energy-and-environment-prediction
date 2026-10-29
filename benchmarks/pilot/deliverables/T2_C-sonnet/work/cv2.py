import os
os.environ["OMP_NUM_THREADS"] = "1"; os.environ["OPENBLAS_NUM_THREADS"] = "1"; os.environ["MKL_NUM_THREADS"] = "1"
import sys, warnings, time
import numpy as np, pandas as pd
from sklearn.linear_model import Ridge
from feat import *
warnings.filterwarnings("ignore")

df5 = clean5(load_raw("../train.csv"))
g = grid15(df5)
y = g["y"]
mod = pd.Series(g.index.hour * 60 + g.index.minute, index=g.index)
wk = pd.Series(g.index.dayofweek < 5, index=g.index)

folds = [("2021-10-26", "2021-11-01"), ("2021-11-02", "2021-11-08"), ("2021-11-09", "2021-11-14"),
         ("2021-11-15", "2021-11-17"), ("2021-12-09", "2021-12-09")]


def rmse(a, b):
    m = a.notna() & b.notna()
    return float(np.sqrt(((a[m] - b[m]) ** 2).mean())), int(m.sum())


class ProfRes:
    def __init__(self, alpha=10.0, use_exog=False, nl=(4, 5, 6, 7, 8), win=8, on_thr=2.0, shrink_prof=False):
        self.alpha, self.use_exog, self.nl, self.win, self.on_thr = alpha, use_exog, nl, win, on_thr

    def _feats(self, idx):
        yy = g["y"]
        pm = mod.map(self.prof)  # profile at each row
        pm = pm.where(wk, np.nan)  # profile only defined for weekdays
        r = yy - pm
        onw = pm > self.on_thr
        r = r.where(onw)
        F = pd.DataFrame(index=g.index)
        for k in self.nl:
            F[f"r{k}"] = r.shift(k)
        F["rm"] = r.shift(4).rolling(self.win, min_periods=1).mean()
        F["cnt"] = r.shift(4).rolling(self.win, min_periods=1).count()
        # state mismatch: profile says on at T-4 but AHU off (valve cmd small)
        on_exp = onw.shift(4)
        on_act = (g["cooling_coil_valve_command"].shift(4) > 15)
        F["mismatch"] = (on_exp & ~on_act).astype(float)
        F = F.fillna(0.0)
        F["pT"] = pm
        if self.use_exog:
            for c in ["dry_bulb_temp", "global_horizontal_solar_radiation", "outdoor_relative_humidity", "air_temperature"]:
                F[c + "_l4"] = g[c].shift(4)
            for c in ["offcoil_air_temp", "cooling_coil_valve_command"]:
                F[c + "_l4"] = g[c].shift(4)
        return F

    def fit(self, tr_idx):
        trd = y.index.isin(tr_idx) & y.notna().values
        yt = y[trd]
        self.prof = yt[wk[trd]].groupby(mod[trd][wk[trd]]).mean()
        F = self._feats(None)
        sel = trd & (F["pT"] > self.on_thr).values & wk.values
        Xs = F[sel].drop(columns="pT")
        self.cols = list(Xs.columns)
        self.mu = Xs.mean(); self.sd = Xs.std().replace(0, 1)
        self.m = Ridge(alpha=self.alpha).fit((Xs - self.mu) / self.sd, (y[sel] - F.loc[sel, "pT"]))
        return self

    def predict(self, idx):
        F = self._feats(None).loc[idx]
        pT = F["pT"].fillna(0.0)
        X = ((F[self.cols] - self.mu) / self.sd).fillna(0.0)
        res = pd.Series(self.m.predict(X), index=idx)
        out = pT + res.where(pT > self.on_thr, 0.0)
        # non-weekday: fall back to persistence of lag-4
        nw = ~wk.loc[idx]
        out = out.where(~nw, g["y"].shift(4).loc[idx].fillna(0.0))
        return out


def cv(make, name):
    allp = pd.Series(np.nan, index=y.index); fr = []
    for a, b in folds:
        te = (y.index >= a) & (y.index < pd.Timestamp(b) + pd.Timedelta("1D"))
        tr_idx = y.index[(y.index < pd.Timestamp(a) - pd.Timedelta("1h"))]
        m = make().fit(tr_idx)
        p = m.predict(y.index[te]); allp[te] = p
        fr.append(rmse(y[te], p)[0])
    pooled = rmse(y[allp.notna()], allp[allp.notna()])
    print(f"{name:40s} folds={np.round(fr,3)} pooled={pooled[0]:.3f} n={pooled[1]}", flush=True)
    return allp


if __name__ == "__main__":
    for a in [1, 10, 100]:
        cv(lambda: ProfRes(alpha=a), f"profres alpha={a}")
    cv(lambda: ProfRes(alpha=10, use_exog=True), "profres exog alpha=10")
    cv(lambda: ProfRes(alpha=100, use_exog=True), "profres exog alpha=100")
    cv(lambda: ProfRes(alpha=10, win=4), "profres win4")
    cv(lambda: ProfRes(alpha=10, win=12), "profres win12")
