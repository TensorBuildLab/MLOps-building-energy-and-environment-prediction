"""The main entry point: one prediction task on one building's data.

Typical flow (an AI agent or an engineer can drive it the same way)::

    p = Project(df, target="AHU1_CLG_KW", horizon="1h", columns={...})
    print(p.check_data())     # read the issues
    # fix what needs judgment (your own code), then p.update(...),
    # or p.accept("issue-id", reason="...") if it is fine as it is
    p.prepare(freq="15min")   # standard, logged cleaning
    results = p.fit()         # time-ordered split, baselines, tuned models
    p.save_run("runs/")       # report, model card, model, predictions, full audit record

Numeric targets (energy, temperature, CO2, ...) are regression tasks. Yes/no
targets (occupancy status, equipment on/off) are classification tasks; the
task type follows from the declared quantity.
"""

from __future__ import annotations

import datetime as _dt
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

import numpy as np
import pandas as pd
from sklearn.base import clone

from ._version import __version__
from .checks import DataReport, check_data, fmt_td
from .deploy import ForecastModel
from .features import audit, build_features, input_drivers, steps_in, suspicious_inputs, target_shifts
from .metrics import PRIMARY_METRIC, evaluate, guideline14, skill_score
from .models import (
    DEFAULT_MODELS,
    Persistence,
    PersistenceClassifier,
    ProfileBaseline,
    ShareOfOnes,
    TrainMean,
    candidates,
    scores,
    tune,
)
from .prepare import PrepareOptions, prepare
from .schema import ColumnSpec, parse_columns, to_time_index
from .split import time_split

CONFIG_VERSION = 1


class UnresolvedIssues(RuntimeError):
    """fit() was called while the data check still has errors nobody has dealt with."""


@dataclass
class Results:
    task: Dict[str, Any]
    split: Dict[str, Any]
    validation: pd.DataFrame
    chosen: str
    chosen_params: Dict[str, Any]
    test: Dict[str, float]
    baseline_name: str
    test_baseline: Dict[str, float]
    skill: float
    guideline14: Optional[Dict[str, Any]]
    predictions: pd.DataFrame
    features: List[Dict[str, Any]]
    model: ForecastModel
    warnings: List[str] = field(default_factory=list)
    leakage_warnings: List[str] = field(default_factory=list)
    interval: Optional[Dict[str, float]] = None  # nominal 90% prediction interval and its test coverage
    drivers: List[Dict[str, Any]] = field(default_factory=list)  # share of accuracy owed to each input
    backtest: Optional[Dict[str, Any]] = None  # rolling-origin blocks: per-block and pooled skill

    def summary(self) -> str:
        t, u = self.task, self.task.get("unit") or ""
        cls = t["task_type"] == "classification"
        lines = [f"Task: {t['description']}",
                 f"Rows used: train {self.split['sizes']['train']}, validation {self.split['sizes']['val']}, "
                 f"test {self.split['sizes']['test']} (time-ordered, gap {self.split['gap']}).",
                 f"Validation results (lower {'Brier score' if cls else 'RMSE'} is better):"]
        keys = (["brier", "accuracy", "balanced_accuracy", "f1", "roc_auc"] if cls
                else ["rmse", "mae", "cvrmse_pct", "nmbe_pct", "r2"])
        cols = ["model"] + [c for c in keys if c in self.validation]
        lines.append(self.validation[cols].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
        m = self.test
        if cls:
            line = (f"Chosen: {self.chosen}. Test: Brier {m['brier']:.3f}, accuracy {m['accuracy']:.3f}, "
                    f"balanced accuracy {m['balanced_accuracy']:.3f}, F1 {m['f1']:.3f}")
            if "roc_auc" in m:
                line += f", ROC AUC {m['roc_auc']:.3f}"
        else:
            line = f"Chosen: {self.chosen}. Test: RMSE {m['rmse']:.3g} {u}, MAE {m['mae']:.3g} {u}"
            if "cvrmse_pct" in m:
                line += f", CV(RMSE) {m['cvrmse_pct']:.1f}%, NMBE {m['nmbe_pct']:.1f}%"
        lines.append(line + ".")
        lines.append(f"Skill vs {self.baseline_name}: {self.skill:.2f} (1 = perfect, 0 = no better than the baseline).")
        if self.guideline14:
            g = self.guideline14
            verdict = "passes" if g["passes"] else "does not pass"
            lines.append(f"ASHRAE Guideline 14 ({g['resolution']}): CV(RMSE) {g['cvrmse_pct']:.1f}% "
                         f"(limit {g['cvrmse_limit']:.0f}%), NMBE {g['nmbe_pct']:.1f}% "
                         f"(limit +/-{g['nmbe_limit']:.0f}%): {verdict}.")
        if self.interval:
            iv = self.interval
            lines.append(f"90% prediction interval: +/-{iv['half_width']:.3g} {u}; it contained "
                         f"{iv['test_coverage']:.0%} of test values.")
        if self.backtest:
            b = self.backtest
            per = ", ".join(f"{x['skill']:.2f}" for x in b["blocks"])
            lines.append(f"Backtest ({len(b['blocks'])} later blocks, refit before each): pooled skill "
                         f"{b['pooled_skill']:.2f} (per block {per}).")
        if self.drivers:
            top = ", ".join(f"{d['input']} {d['share']:.0%}" for d in self.drivers[:4])
            lines.append(f"Main drivers of accuracy: {top}.")
        for w in self.leakage_warnings + self.warnings:
            lines.append(f"Warning: {w}")
        return "\n".join(lines)

    __str__ = summary
    __repr__ = summary


class Project:
    def __init__(self, data: pd.DataFrame, target: str,
                 columns: Mapping[str, Union[str, Mapping[str, Any], ColumnSpec]],
                 horizon: Union[int, str, pd.Timedelta] = 0, timestamp: Optional[str] = None,
                 timestamp_format: Optional[str] = None, name: Optional[str] = None,
                 task: Optional[str] = None, intended_use: str = "",
                 holidays: Optional[Sequence[Any]] = None, tz: Optional[str] = None):
        """
        data:      the building data, indexed by time (or pass `timestamp` = the time column).
        target:    the column to predict: any declared numeric or yes/no point.
        columns:   what every column you want to use means, e.g.
                   {"RM204_ZN_T": "zone_air_temperature [degF]", "OAT": "outdoor_air_temperature [degF]"}.
                   Undeclared columns are ignored.
        horizon:   how far ahead to predict, e.g. "1h" or 4 (steps). 0 means estimate the
                   target from inputs measured at the same moment (virtual sensor).
        timestamp_format: e.g. "%m/%d/%Y %I:%M:%S %p". Recommended: avoids day/month mix-ups.
        task:      "regression" or "classification"; by default chosen from the target's quantity.
        intended_use: one sentence on what the predictions are for (goes into the model card).
        holidays:  dates the building runs as on a holiday (closures, public holidays). Becomes an
                   input known in advance. Deciding which dates count is a judgment call.
        tz:        the building's time zone, e.g. "Europe/Copenhagen". Needed when timestamps carry
                   UTC offsets that change with daylight saving.
        """
        self.name = name or f"{target}"
        self.log: List[Dict[str, Any]] = []
        self.timestamp, self.timestamp_format, self.tz = timestamp, timestamp_format, tz
        self.raw, event = to_time_index(data, timestamp, timestamp_format, tz=tz)
        if event:
            self._event("timestamps", event)
        self.specs: Dict[str, ColumnSpec] = parse_columns(columns)
        if target not in self.specs:
            raise ValueError(f"Declare the target too, e.g. columns={{'{target}': '<quantity> [<unit>]', ...}}.")
        self.target = target
        h = horizon
        negative = (h < 0) if isinstance(h, (int, np.integer)) else (pd.Timedelta(h) < pd.Timedelta(0))
        if negative:
            raise ValueError("The horizon cannot be negative.")
        self.horizon = horizon
        inferred = "classification" if self.specs[target].q.kind == "binary" else "regression"
        if task not in (None, "regression", "classification"):
            raise ValueError("task must be 'regression' or 'classification'.")
        self.task = task or inferred
        self.intended_use = intended_use
        self.holidays = sorted({pd.Timestamp(d).strftime("%Y-%m-%d") for d in (holidays or [])})
        self.accepted: Dict[str, str] = {}
        self.previous_acceptances: Dict[str, str] = {}  # decisions taken on earlier data (informational)
        self.notes: List[str] = []
        self.report_: Optional[DataReport] = None
        self.data: Optional[pd.DataFrame] = None
        self.prepare_log: List[Dict[str, Any]] = []
        self.prepare_options: Optional[PrepareOptions] = None
        self.fit_options: Dict[str, Any] = {}
        self.results: Optional[Results] = None

    # ----- configuration (for reproduction and retraining) -------------------
    def config(self) -> Dict[str, Any]:
        """Everything needed to re-run this task on the same or newer data."""
        h = self.horizon
        return {
            "config_version": CONFIG_VERSION,
            "name": self.name,
            "target": self.target,
            "task": self.task,
            "horizon": int(h) if isinstance(h, (int, np.integer)) else str(h),
            "columns": {k: v.to_dict() for k, v in self.specs.items()},
            "timestamp": self.timestamp,
            "timestamp_format": self.timestamp_format,
            "tz": self.tz,
            "intended_use": self.intended_use,
            "holidays": list(self.holidays),
            "prepare": self.prepare_options.to_dict() if self.prepare_options else None,
            "fit": dict(self.fit_options),
            "accepted": dict(self.accepted),
            "notes": list(self.notes),
        }

    @classmethod
    def from_config(cls, data: pd.DataFrame, config: Mapping[str, Any], carry_decisions: bool = True,
                    trust_accepted: bool = False) -> "Project":
        """Rebuild a project from `config()` output (or a run record's "config").

        carry_decisions: keep notes (marked as carried over) and show earlier acceptances.
        trust_accepted: re-apply earlier acceptances. Only for the same data (reproduction). On new
            data every error must be decided again: accepting "column RH missing" must not
            silently cover "columns OAT and RH missing".
        """
        columns = {k: {kk: vv for kk, vv in v.items() if kk != "name"} for k, v in config["columns"].items()}
        p = cls(data, config["target"], columns, horizon=config["horizon"], timestamp=config.get("timestamp"),
                timestamp_format=config.get("timestamp_format"), name=config.get("name"),
                task=config.get("task"), intended_use=config.get("intended_use", ""),
                holidays=config.get("holidays"), tz=config.get("tz"))
        if config.get("prepare"):
            p.prepare_options = PrepareOptions(**config["prepare"])
        p.fit_options = dict(config.get("fit") or {})
        for k, v in (config.get("accepted") or {}).items():
            if trust_accepted:
                p.accepted[k] = v
            elif carry_decisions:
                p.previous_acceptances[k] = v
        if carry_decisions:
            for n in config.get("notes") or []:
                p.notes.append(n if n.startswith("[carried over]") else f"[carried over] {n}")
        p._event("config", "Project rebuilt from a saved configuration.")
        return p

    # ----- bookkeeping -------------------------------------------------
    def _event(self, kind: str, detail: str) -> None:
        self.log.append({"time": _dt.datetime.now().isoformat(timespec="seconds"), "kind": kind, "detail": detail})

    def note(self, text: str) -> None:
        """Record a decision and why (e.g. 'Dropped AHU2: disconnected during retrofit'). Goes into the run record."""
        self.notes.append(text)
        self._event("note", text)

    def accept(self, issue_id: str, reason: str) -> None:
        """Accept a reported error as it is. A written reason is required and kept in the run record."""
        if not reason or len(reason.strip()) < 10:
            raise ValueError("Give a real reason (at least a short sentence) for accepting an issue.")
        if self.report_ is not None:
            self.report_.get(issue_id)  # raises KeyError for an unknown id
        self.accepted[issue_id] = reason.strip()
        self._event("accept", f"{issue_id}: {reason.strip()}")

    def update(self, data: Optional[pd.DataFrame] = None,
               columns: Optional[Mapping[str, Any]] = None, drop: Sequence[str] = (),
               note: Optional[str] = None) -> None:
        """Swap in fixed data, corrected or new declarations, or drop columns. Checks run again before fitting."""
        if data is not None:
            if not isinstance(data.index, pd.DatetimeIndex):
                raise ValueError("Updated data needs a DatetimeIndex.")
            self.raw = data.copy()
        if columns is not None:
            self.specs.update(parse_columns(columns))
        for c in drop:
            if c == self.target:
                raise ValueError("The target cannot be dropped.")
            self.specs.pop(c, None)
        self.report_, self.data, self.results = None, None, None
        self._event("update", note or "Data or declarations updated.")
        if note:
            self.notes.append(note)

    # ----- the workflow --------------------------------------------------
    @property
    def mode(self) -> str:
        h = self.horizon
        zero = (isinstance(h, (int, np.integer)) and h == 0) or (
            not isinstance(h, (int, np.integer)) and pd.Timedelta(h) == pd.Timedelta(0))
        return "estimate" if zero else "forecast"

    def check_data(self, stuck_hours: float = 6.0) -> DataReport:
        self.report_ = check_data(self.raw, self.specs, self.target, stuck_hours=stuck_hours)
        self._event("check", f"{len(self.report_.errors)} errors, {len(self.report_.warnings)} warnings")
        return self.report_

    def prepare(self, freq: Optional[str] = None, **options: Any) -> pd.DataFrame:
        """Standard cleaning (see bemlops.prepare). Options: mask_stuck, mask_spikes, fill_limit, ..."""
        if freq is None and not options and self.prepare_options is not None:
            opts = self.prepare_options  # e.g. from a saved configuration
        else:
            opts = PrepareOptions(freq=freq, **options)
        self.prepare_options = opts
        self.data, self.prepare_log = prepare(self.raw, self.specs, self.target, opts)
        self._event("prepare", f"{len(self.data)} rows on a {fmt_td(self.step)} grid")
        return self.data

    @property
    def step(self) -> pd.Timedelta:
        if self.data is None:
            raise RuntimeError("Run prepare() first.")
        return pd.Timedelta(self.data.index[1] - self.data.index[0])

    @property
    def horizon_steps(self) -> int:
        h = self.horizon
        if isinstance(h, (int, np.integer)):
            return int(h)
        ratio = pd.Timedelta(h) / self.step
        if abs(ratio - round(ratio)) > 1e-9:
            raise ValueError(f"Horizon {h} is not a whole number of {self.step} steps.")
        return int(round(ratio))

    def unresolved(self) -> List[Any]:
        if self.report_ is None:
            self.check_data()
        return [i for i in self.report_.errors if i.id not in self.accepted]

    def fit(self, models: Optional[Sequence[str]] = None, n_iter: Optional[int] = None,
            fractions=None, random_state: Optional[int] = None,
            custom_models: Optional[Mapping[str, Any]] = None, backtest_blocks: Optional[int] = None,
            refit_all: Optional[bool] = None) -> Results:
        """Choose and evaluate a model.

        custom_models: {name: (estimator, search_space)} added to the candidates, e.g. a model the
            agent built. It is evaluated under exactly the same rules as the built-in ones.
        backtest_blocks: also refit the chosen model before each of this many later blocks and score
            each block (rolling origin), so one unusual test period cannot decide the verdict alone.
        refit_all: after evaluation, refit the chosen configuration on all data (including the test
            period) for deployment. The reported metrics remain those of the evaluated model; the record
            says which data the deployed model saw.
        """
        # Saved fit options (e.g. from a configuration) fill in anything not given here.
        saved = self.fit_options
        explicit = models or saved.get("models")
        models = tuple(explicit or DEFAULT_MODELS[self.task])
        backtest_blocks = backtest_blocks if backtest_blocks is not None else saved.get("backtest_blocks", 3)
        refit_all = bool(refit_all if refit_all is not None else saved.get("refit_all", False))
        n_iter = n_iter if n_iter is not None else saved.get("n_iter", 10)
        fractions = tuple(fractions or saved.get("fractions") or (0.7, 0.15, 0.15))
        random_state = random_state if random_state is not None else saved.get("random_state", 0)
        self.fit_options = {"models": list(models) if explicit else None, "n_iter": n_iter,
                            "fractions": list(fractions), "random_state": random_state,
                            "backtest_blocks": backtest_blocks, "refit_all": refit_all}

        blocking = self.unresolved()
        if blocking:
            lines = ["The data check found errors that need a decision before fitting:"]
            for i in blocking:
                lines.append(f"  - {i.id}: {i.message}" + (f" ({i.fix})" if i.fix else ""))
            lines.append("Fix the data or declarations and call update(...), "
                         "or accept an issue with accept(id, reason='...').")
            raise UnresolvedIssues("\n".join(lines))
        if self.data is None:
            self.prepare()

        data, step, h, target, task = self.data, self.step, self.horizon_steps, self.target, self.task
        cls = task == "classification"
        lags = target_shifts(h, step, len(data)) if h > 0 else []
        X, y, feats = build_features(data, target, self.specs, h, step, target_lags=lags,
                                     holidays=self.holidays)
        audit(feats, target, h)
        leak_warnings = suspicious_inputs(X, y, feats, target)
        warnings_: List[str] = []

        usable = y.notna().to_numpy()
        Xu, yu = X[usable], y[usable]
        if cls:
            yu = (yu >= 0.5).astype(int)  # resampled yes/no values are shares of the interval
        if len(yu) < 200:
            raise ValueError(f"Only {len(yu)} rows have a target value; at least 200 are needed.")
        gap = h * step
        sp = time_split(Xu.index, fractions, gap=gap)
        Xtr, ytr, Xva, yva, Xte, yte = Xu[sp.train], yu[sp.train], Xu[sp.val], yu[sp.val], Xu[sp.test], yu[sp.test]
        if cls and min(ytr.nunique(), yva.nunique()) < 2:
            raise ValueError("Training or validation data contain only one class; use more data.")
        for part, n_rows in (("validation", len(yva)), ("test", len(yte))):
            if n_rows < 100:
                warnings_.append(f"Only {n_rows} {part} rows: results are noisy. Use more data or a shorter horizon.")

        if h > 0:
            P = PersistenceClassifier if cls else Persistence
            baselines = {"persistence": P(f"{target}__t-{h}")}
            day = steps_in("1D", step)
            if f"{target}__t-{day}" in X.columns:
                baselines["same_time_yesterday"] = P(f"{target}__t-{day}")
        else:
            baselines = {"share_of_ones" if cls else "training_mean": ShareOfOnes() if cls else TrainMean()}
        if not cls:
            baselines["time_of_day_profile"] = ProfileBaseline()

        primary = PRIMARY_METRIC[task]
        rows, fitted, val_models = [], {}, {}
        for name, est in baselines.items():
            est.fit(Xtr, ytr)
            rows.append({"model": name, "type": "baseline", **evaluate(yva, scores(est, Xva, task), task),
                         "params": {}})
            fitted[name] = (est, {})
            val_models[name] = est
        anchor = f"{target}__t-{h}" if (h > 0 and not cls) else None
        pool = candidates(random_state, task, anchor=anchor)
        pool.update(dict(custom_models or {}))
        if not explicit:
            models = tuple(m for m in models if m in pool) + tuple(
                k for k in (custom_models or {}) if k not in models)
        for name in models:
            if name not in pool:
                raise ValueError(f"Unknown model '{name}' for {task}. Available: {sorted(pool)}")
            est, space = pool[name]
            best, params, cv_score = tune(est, space, Xtr, ytr, gap_steps=h, n_iter=n_iter,
                                          random_state=random_state, task=task)
            rows.append({"model": name, "type": "ml", **evaluate(yva, scores(best, Xva, task), task),
                         "cv_score": cv_score, "params": params})
            fitted[name] = (est, params)
            val_models[name] = best
        validation = pd.DataFrame(rows).sort_values(primary).reset_index(drop=True)
        # Skill is measured against the strongest no-ML baseline on validation data.
        ref_name = str(validation[validation["type"] == "baseline"].iloc[0]["model"])
        chosen = str(validation.iloc[0]["model"])
        base_est, params = fitted[chosen]

        trval = sp.train | sp.val
        final = clone(base_est).set_params(**params) if params else clone(base_est)
        final.fit(Xu[trval], yu[trval])
        pred = scores(final, Xte, task)
        ref = clone(baselines[ref_name]).fit(Xu[trval], yu[trval])
        ref_pred = scores(ref, Xte, task)
        test_m = evaluate(yte, pred, task)
        ref_m = evaluate(yte, ref_pred, task)
        skill = skill_score(test_m[primary], ref_m[primary])

        q = self.specs[target].q
        g14 = None
        col = "probability" if cls else "predicted"
        predictions = pd.DataFrame({"actual": yte, col: pred, ref_name: ref_pred}, index=Xte.index)
        interval = None
        if not cls:
            # Split-conformal style: the width comes from validation errors of the chosen model trained
            # on the training period only; its coverage is then checked on the untouched test period.
            resid = np.abs(np.asarray(yva, dtype=float) - scores(val_models[chosen], Xva, task))
            half = float(np.nanquantile(resid, 0.9))
            lo_b, hi_b = q.plausible
            # Clip to the physically plausible range, but never so far that the interval excludes the
            # prediction itself (a model can predict slightly below zero power).
            lower = np.minimum(np.maximum(pred - half, lo_b), pred)
            upper = np.maximum(np.minimum(pred + half, hi_b), pred)
            yt = np.asarray(yte, dtype=float)
            interval = {"nominal": 0.9, "half_width": half,
                        "test_coverage": float(np.mean((yt >= lower) & (yt <= upper)))}
            predictions["lower"], predictions["upper"] = lower, upper
        drivers = input_drivers(final, Xte, yte, feats, target, task, random_state)
        backtest = (self._backtest(Xu, yu, sp, base_est, params, baselines[ref_name], task, primary, gap,
                                   backtest_blocks) if backtest_blocks else None)
        if not cls and q.headline_metric == "cvrmse" and step <= pd.Timedelta("1h"):
            # Guideline 14's hourly criteria, applied to hourly totals or means.
            g14 = guideline14(predictions["actual"], predictions["predicted"], aggregate=q.aggregate)
        if chosen in baselines:
            warnings_.append(f"No machine-learning model beat the '{chosen}' baseline on validation data. "
                             f"Look for better inputs before deploying anything more complex.")
        elif skill < 0.05:
            warnings_.append(f"The model is barely better than {ref_name} on test data (skill {skill:.2f}).")

        train_rows = data.loc[: sp.bounds["val"][1]]
        ranges = {}
        for c in self.specs:
            if c != target and c in train_rows.columns and train_rows[c].notna().any():
                lo, hi = np.nanpercentile(train_rows[c], [1, 99])
                ranges[c] = (float(lo), float(hi))
        target_range = (float(np.nanmin(train_rows[target])), float(np.nanmax(train_rows[target])))
        unit = q.canonical_unit
        horizon_text = (f"{fmt_td(h * step)} ahead ({h} step(s) of {fmt_td(step)})" if h > 0
                        else "at the same moment as its inputs (estimation / virtual sensor)")
        kind = "yes/no " if cls else ""
        task_info = {"target": target, "quantity": q.name, "unit": unit, "mode": self.mode, "task_type": task,
                     "horizon_steps": h, "step": str(step),
                     "description": f"{self.mode} {kind}{target} ({q.name}, {unit}) {horizon_text}"}
        deployed, deployed_end = final, sp.bounds["val"][1]
        if refit_all:
            deployed = clone(base_est).set_params(**params) if params else clone(base_est)
            deployed.fit(Xu, yu)
            deployed_end = Xu.index[-1]
            warnings_.append("Deployed model refitted on all data, including the test period; the reported "
                             "test metrics are those of the model trained before it.")
        model = ForecastModel(
            target=target, specs=dict(self.specs), horizon=h, step=step,
            prepare_options=self.prepare_options, estimator=deployed, model_name=chosen,
            feature_names=list(X.columns), target_lags=lags, include_doy="doy_sin" in X.columns,
            input_ranges=ranges, test_error=test_m[primary], train_end=deployed_end,
            version=__version__, trained_at=_dt.datetime.now().isoformat(timespec="seconds"), unit=unit,
            task=task, timestamp=self.timestamp, timestamp_format=self.timestamp_format,
            config=self.config(), train_start=sp.bounds["train"][0], target_range=target_range,
            holidays=list(self.holidays), interval_half_width=interval["half_width"] if interval else None,
            tz=self.tz, index_tz=None if self.raw.index.tz is None else str(self.raw.index.tz))
        self.results = Results(
            task=task_info,
            split={"sizes": sp.sizes(), "gap": fmt_td(gap),
                   "bounds": {k: (str(a), str(b)) for k, (a, b) in sp.bounds.items()}},
            validation=validation, chosen=chosen, chosen_params=params, test=test_m,
            baseline_name=ref_name, test_baseline=ref_m, skill=skill, guideline14=g14,
            predictions=predictions, features=[f.to_dict() for f in feats], model=model,
            warnings=warnings_, leakage_warnings=leak_warnings, interval=interval, drivers=drivers,
            backtest=backtest)
        self._event("fit", f"chosen {chosen}, test {primary} {test_m[primary]:.4g}")
        return self.results

    @staticmethod
    def _backtest(Xu, yu, sp, base_est, params, baseline, task, primary, gap, k) -> Optional[Dict[str, Any]]:
        """Rolling origin over the period after training: k blocks, refitting before each on all earlier
        rows (minus the horizon gap). The validation period, used to choose the model, is part of these
        blocks; the untouched single test period remains the primary result."""
        times = Xu.index
        later = np.flatnonzero(np.asarray(times > sp.bounds["train"][1]))
        if len(later) < 50 * k:
            return None
        blocks, ys, ms, bs = [], [], [], []
        for chunk in np.array_split(later, k):
            t0 = times[chunk[0]]
            train = np.asarray(times < t0 - gap)
            if train.sum() < 100:
                continue
            m = clone(base_est).set_params(**params) if params else clone(base_est)
            m.fit(Xu[train], yu[train])
            b = clone(baseline).fit(Xu[train], yu[train])
            yb = yu.iloc[chunk]
            pm, pb = scores(m, Xu.iloc[chunk], task), scores(b, Xu.iloc[chunk], task)
            em, eb = evaluate(yb, pm, task)[primary], evaluate(yb, pb, task)[primary]
            blocks.append({"from": str(t0), "to": str(times[chunk[-1]]), "rows": int(len(chunk)),
                           primary: em, f"baseline_{primary}": eb, "skill": skill_score(em, eb)})
            ys.append(yb.to_numpy())
            ms.append(pm)
            bs.append(pb)
        if not blocks:
            return None
        y_all, m_all, b_all = np.concatenate(ys), np.concatenate(ms), np.concatenate(bs)
        em, eb = evaluate(y_all, m_all, task)[primary], evaluate(y_all, b_all, task)[primary]
        return {"blocks": blocks, f"pooled_{primary}": em, f"pooled_baseline_{primary}": eb,
                "pooled_skill": skill_score(em, eb)}

    def save_run(self, out_dir: Union[str, Path] = "runs") -> Path:
        """Write the report, model card, model, test predictions and the full audit record to a new folder."""
        from .report import write_run

        return write_run(self, Path(out_dir))
