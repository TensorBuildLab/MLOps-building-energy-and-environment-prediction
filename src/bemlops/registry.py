"""A file-based model registry: versions, stages, promotion gates, champion vs challenger, rollback.

    registry/<name>/
        registry.json      every version, its stage and gate results, and an event log
        v1/, v2/, ...      the run folder contents of each registered version

Stages: "candidate" (registered), "production" (at most one), "archived".
A version reaches production only through ``promote``, which enforces the
promotion gates; overriding them needs a written reason and is logged.
"""

from __future__ import annotations

import datetime as _dt
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from .deploy import ForecastModel, load_model
from .governance import PromotionPolicy, check_gates, gates_passed
from .metrics import PRIMARY_METRIC, evaluate

_FILES = ("model.joblib", "run.json", "report.md", "model_card.md", "test_predictions.csv",
          "test_timeseries.png", "test_scatter.png")


class PromotionRefused(RuntimeError):
    """A version did not pass the promotion gates."""


def _now() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


class Registry:
    def __init__(self, root: Union[str, Path], policy: Optional[PromotionPolicy] = None):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.policy = policy or PromotionPolicy()

    # ----- storage -----------------------------------------------------------
    def _index_path(self, name: str) -> Path:
        return self.root / name / "registry.json"

    def _load(self, name: str) -> Dict[str, Any]:
        path = self._index_path(name)
        if not path.exists():
            return {"name": name, "versions": [], "events": []}
        return json.loads(path.read_text(encoding="utf-8"))

    def _save(self, name: str, index: Dict[str, Any]) -> None:
        path = self._index_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(index, indent=2), encoding="utf-8")
        tmp.replace(path)

    def _entry(self, index: Dict[str, Any], version: int) -> Dict[str, Any]:
        for e in index["versions"]:
            if e["version"] == version:
                return e
        raise KeyError(f"No version {version} of '{index['name']}'.")

    def names(self) -> List[str]:
        return sorted(p.parent.name for p in self.root.glob("*/registry.json"))

    # ----- lifecycle -----------------------------------------------------------
    def register(self, run_folder: Union[str, Path], name: Optional[str] = None) -> Dict[str, Any]:
        """Add a saved run as a new candidate version. Gates are evaluated and stored."""
        run_folder = Path(run_folder)
        record = json.loads((run_folder / "run.json").read_text(encoding="utf-8"))
        name = name or record["config"]["name"]
        index = self._load(name)
        if index["versions"]:
            first, new = index["versions"][0]["task"], record["task"]
            for k in ("target", "horizon_steps", "step", "task_type"):
                if first.get(k) != new.get(k):
                    raise ValueError(f"Version for '{name}' has {k}={new.get(k)!r}, but earlier versions have "
                                     f"{first.get(k)!r}. Register it under a different name.")
        version = max([e["version"] for e in index["versions"]], default=0) + 1
        dest = self.root / name / f"v{version}"
        dest.mkdir(parents=True)
        for f in _FILES:
            if (run_folder / f).exists():
                shutil.copy2(run_folder / f, dest / f)
        gates = check_gates(record, self.policy)
        entry = {
            "version": version,
            "stage": "candidate",
            "registered_at": _now(),
            "source_run": str(run_folder),
            "task": record["task"],
            "train_period": [record["split"]["bounds"]["train"][0], record["split"]["bounds"]["val"][1]],
            "test": record["test"],
            "data_fingerprint": record["data"]["raw_fingerprint"],
            "code_commit": record["run"]["environment"].get("code_commit"),
            "gates": gates,
            "gates_passed": gates_passed(gates),
        }
        index["versions"].append(entry)
        index["events"].append({"time": _now(), "action": "register", "version": version,
                                "gates_passed": entry["gates_passed"]})
        self._save(name, index)
        return entry

    def production(self, name: str) -> Optional[Dict[str, Any]]:
        for e in self._load(name)["versions"]:
            if e["stage"] == "production":
                return e
        return None

    def promote(self, name: str, version: int, reason: str = "", force: bool = False,
                action: str = "promote") -> Dict[str, Any]:
        """Make `version` the production model. Refused if a gate fails, unless forced with a reason."""
        index = self._load(name)
        entry = self._entry(index, version)
        # Re-check the gates under the registry's current policy (it may be stricter than at registration).
        run_json = self.root / name / f"v{version}" / "run.json"
        if run_json.exists():
            entry["gates"] = check_gates(json.loads(run_json.read_text(encoding="utf-8")), self.policy)
            entry["gates_passed"] = gates_passed(entry["gates"])
        if not entry["gates_passed"]:
            failed = {k: v["detail"] for k, v in entry["gates"].items() if not v["passed"]}
            if not force:
                raise PromotionRefused(f"Version {version} of '{name}' failed promotion gates: {failed}")
            if len(reason.strip()) < 10:
                raise ValueError("Overriding the gates needs a written reason.")
        for e in index["versions"]:
            if e["stage"] == "production":
                e["stage"] = "archived"
        entry["stage"] = "production"
        index["events"].append({"time": _now(), "action": action, "version": version, "reason": reason,
                                "forced": bool(force and not entry["gates_passed"])})
        self._save(name, index)
        return entry

    def rollback(self, name: str, version: int, reason: str, force: bool = False) -> Dict[str, Any]:
        """Put an earlier version back into production (e.g. after a bad release)."""
        if len(reason.strip()) < 10:
            raise ValueError("A rollback needs a written reason.")
        return self.promote(name, version, reason=reason, force=force, action="rollback")

    def load(self, name: str, version: Optional[int] = None) -> ForecastModel:
        """The production model, or a specific version."""
        if version is None:
            entry = self.production(name)
            if entry is None:
                raise KeyError(f"'{name}' has no production model yet.")
            version = entry["version"]
        return load_model(self.root / name / f"v{version}" / "model.joblib")

    def history(self, name: str) -> pd.DataFrame:
        rows = []
        for e in self._load(name)["versions"]:
            metric = PRIMARY_METRIC.get(e["task"].get("task_type", "regression"))
            rows.append({"version": e["version"], "stage": e["stage"], "registered_at": e["registered_at"],
                         "train_period": " to ".join(e["train_period"]), metric: e["test"]["model"].get(metric),
                         "skill": e["test"].get("skill"), "gates_passed": e["gates_passed"]})
        return pd.DataFrame(rows)

    def events(self, name: str) -> List[Dict[str, Any]]:
        return self._load(name)["events"]

    # ----- champion vs challenger ---------------------------------------------
    def compare(self, name: str, challenger: int, data: pd.DataFrame, champion: Optional[int] = None,
                margin: float = 0.0) -> Dict[str, Any]:
        """Score champion and challenger on the same rows, after both models' training periods ended.

        The challenger wins only if its error is lower by more than `margin` (a fraction, e.g. 0.02).
        """
        champ_entry = self.production(name) if champion is None else self._entry(self._load(name), champion)
        if champ_entry is None:
            raise KeyError(f"'{name}' has no production model to compare against.")
        champ = self.load(name, champ_entry["version"])
        chall = self.load(name, challenger)
        # Only rows whose forecasts were made after both training periods ended (plus the horizon gap).
        start = max(pd.Timestamp(champ.train_end), pd.Timestamp(chall.train_end)) + chall.horizon * chall.step
        task = chall.task
        metric = PRIMARY_METRIC[task]
        col = "probability" if task == "classification" else "predicted"
        a = champ.predict(data, future=False, validate=False)
        b = chall.predict(data, future=False, validate=False)
        rows = pd.concat({"actual": b["actual"], "champion": a[col], "challenger": b[col]}, axis=1)
        rows = rows[rows.index > start].dropna()
        if len(rows) < 50:
            raise ValueError(f"Only {len(rows)} rows after {start} to compare on; need at least 50.")
        e_champ = evaluate(rows["actual"], rows["champion"], task)[metric]
        e_chall = evaluate(rows["actual"], rows["challenger"], task)[metric]
        better = e_chall < e_champ * (1 - margin)
        result = {"metric": metric, "from": str(start), "rows": len(rows),
                  "champion": {"version": champ_entry["version"], metric: e_champ},
                  "challenger": {"version": challenger, metric: e_chall},
                  "challenger_better": bool(better)}
        index = self._load(name)
        index["events"].append({"time": _now(), "action": "compare", **result})
        self._save(name, index)
        return result
