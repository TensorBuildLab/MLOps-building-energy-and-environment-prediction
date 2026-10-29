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



from sklearn.ensemble import HistGradientBoostingRegressor
EXOG = ["dry_bulb_temp", "global_horizontal_solar_radiation", "outdoor_relative_humidity", "air_temperature", "offcoil_air_temp", "cooling_coil_valve_command"]


class ProfRes:
    def __init__(self, alpha=30.0, exog=EXOG, nl=(4, 5, 6, 7, 8), win=8, on_thr=2.0, start=None, gate=False,
                 kind="ridge", exog_lags=(4,), fanE=False, wt_decay=None):
        self.alpha, self.exog, self.nl, self.win, self.on_thr = alpha, exog, nl, win, on_thr
        self.start, self.gate, self.kind, self.exog_lags, self.fanE = start, gate, kind, exog_lags, fanE

    def _feats(self):
        pm = mod.map(self.prof).where(wk, np.nan)
        r = (g["y"] - pm).where(pm > self.on_thr)
        F = pd.DataFrame(index=g.index)
        for k in self.nl:
            F[f"r{k}"] = r.shift(k)
        F["rm"] = r.shift(4).rolling(self.win, min_periods=1).mean()
        F["cnt"] = r.shift(4).rolling(self.win, min_periods=1).count()
        F = F.fillna(0.0)
        F["pT"] = pm
        for c in self.exog:
            for k in self.exog_lags:
                F[f"{c}_l{k}"] = g[c].shift(k)
        if self.fanE:
            F["fanE_l4"] = g["ahu_fan_energy"].shift(4)
        return F

    def fit(self, tr_idx):
        trd = y.index.isin(tr_idx) & y.notna().values
        if self.start: trd &= (y.index >= self.start)
        yt = y[trd]
        self.prof = yt[wk[trd]].groupby(mod[trd][wk[trd]]).mean()
        F = self._feats()
        sel = trd & (F["pT"] > self.on_thr).values & wk.values
        Xs = F[sel].drop(columns="pT")
        self.cols = list(Xs.columns)
        self.mu = Xs.mean(); self.sd = Xs.std().replace(0, 1)
        Z = ((Xs - self.mu) / self.sd).fillna(0.0)
        rt = (y[sel] - F.loc[sel, "pT"])
        if self.kind == "ridge":
            self.m = Ridge(alpha=self.alpha).fit(Z, rt)
        else:
            self.m = HistGradientBoostingRegressor(max_iter=80, learning_rate=0.05, max_depth=3, min_samples_leaf=25, l2_regularization=2.0, random_state=0).fit(Z, rt)
        return self

    def predict(self, idx):
        F = self._feats().loc[idx]
        pT = F["pT"].fillna(0.0)
        Z = ((F[self.cols] - self.mu) / self.sd).fillna(0.0)
        res = pd.Series(self.m.predict(Z), index=idx)
        out = pT + res.where(pT > self.on_thr, 0.0)
        if self.gate:
            pm4 = mod.map(self.prof).where(wk, np.nan).shift(4)
            act = (g["cooling_coil_valve_command"].shift(4) > 10)
            # profile says AHU on 1 h before, but it was actually off -> off-schedule day: persist off state
            mism = (pm4 > self.on_thr) & ~act
            out = out.where(~mism.loc[idx].fillna(False), 0.0)
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
    base = cv(lambda: ProfRes(), "ridge exog a=30")
    cv(lambda: ProfRes(gate=True), "ridge exog a=30 gate")
    cv(lambda: ProfRes(start="2021-09-14"), "ridge exog a=30 start0914")
    cv(lambda: ProfRes(exog_lags=(4, 6)), "ridge exog lags 4,6")
    cv(lambda: ProfRes(exog=EXOG + ["wind_speed", "indoor_co2"]), "ridge +wind,co2")
    cv(lambda: ProfRes(exog=[]), "ridge no exog")
    cv(lambda: ProfRes(fanE=True), "ridge +fanE")
    cv(lambda: ProfRes(alpha=300), "ridge a=300")
    ph = cv(lambda: ProfRes(kind="hgb"), "hgb residual")
    # error by hour for base
    e = (y - base).dropna()
    print((e ** 2).groupby(e.index.hour).mean().pow(0.5).round(2).to_string())
    pm = y.groupby(mod[wk]).mean()
