"""Automated pipelines: train from a configuration, retrain with champion/challenger, reproduce a run.

These are what a scheduler (cron, Airflow, a GitHub Action) calls. Every
step still goes through the same checks: a pipeline stops on unresolved
data errors instead of training on bad data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

import numpy as np
import pandas as pd

from .project import Project
from .registry import Registry
from .report import fingerprint


@dataclass
class TrainOutcome:
    project: Project
    run_folder: Path
    registry_entry: Optional[Dict[str, Any]] = None


def train(data: pd.DataFrame, config: Mapping[str, Any], out_dir: Union[str, Path] = "runs",
          registry: Optional[Registry] = None, name: Optional[str] = None) -> TrainOutcome:
    """Check, prepare, fit and save one task from a configuration; optionally register it."""
    p = Project.from_config(data, config)
    p.check_data()
    p.prepare()
    p.fit()
    folder = p.save_run(Path(out_dir))
    entry = registry.register(folder, name or p.name) if registry is not None else None
    return TrainOutcome(p, folder, entry)


def retrain(data: pd.DataFrame, registry: Registry, name: str, out_dir: Union[str, Path] = "runs",
            margin: float = 0.0, promote: bool = True) -> Dict[str, Any]:
    """Continuous training: train a challenger on newer data with the production model's configuration,
    compare both on data neither has trained on, and promote the challenger only if it passes the
    gates and wins."""
    champion = registry.load(name)
    outcome = train(data, champion.config, out_dir, registry, name)
    entry = outcome.registry_entry
    comparison = registry.compare(name, entry["version"], outcome.project.raw, margin=margin)
    promoted = False
    if promote and entry["gates_passed"] and comparison["challenger_better"]:
        m = comparison["metric"]
        registry.promote(name, entry["version"],
                         reason=f"Retrained; {m} {comparison['challenger'][m]:.4g} vs "
                                f"{comparison['champion'][m]:.4g} on {comparison['rows']} unseen rows.")
        promoted = True
    return {"challenger_version": entry["version"], "gates_passed": entry["gates_passed"],
            "comparison": comparison, "promoted": promoted, "run_folder": str(outcome.run_folder)}


def reproduce(run_json: Union[str, Path], data: pd.DataFrame, tolerance: float = 1e-9) -> Dict[str, Any]:
    """Re-run a saved run from its record and check that the data and the results match.

    `data` must be the same input the original Project received (after any custom
    cleaning the agent did before handing it over).
    """
    record = json.loads(Path(run_json).read_text(encoding="utf-8"))
    p = Project.from_config(data, record["config"])
    data_match = fingerprint(p.raw) == record["data"]["raw_fingerprint"]
    p.check_data()
    p.prepare()
    r = p.fit()
    original = record["test"]["model"]
    diffs = [abs(float(r.test[k]) - float(v)) for k, v in original.items()
             if v is not None and k in r.test and np.isfinite(r.test[k])]
    max_diff = max(diffs) if diffs else float("nan")
    return {"data_matches": data_match, "same_model": r.chosen == record["chosen_model"]["name"],
            "metrics_match": bool(max_diff <= tolerance), "max_abs_difference": max_diff,
            "original": original, "reproduced": r.test}
