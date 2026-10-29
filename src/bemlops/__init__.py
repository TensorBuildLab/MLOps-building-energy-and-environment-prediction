"""bemlops: machine-learning operations for building energy and indoor-environment prediction.

An AI agent (or an engineer) handles the messy, building-specific parts in its
own code. bemlops makes sure the parts that must never go wrong are right:
declared units checked against physics, time-ordered splits, no leakage,
honest baselines, standard metrics, gated promotion to production,
monitoring, and a full record of every run.
"""

from ._version import __version__
from .checks import DataReport, Issue, check_data
from .deploy import DriftReport, ForecastModel, InvalidInputData, load_model
from .features import LeakageError
from .governance import PromotionPolicy, check_gates
from .pipeline import reproduce, retrain, train
from .project import Project, Results, UnresolvedIssues
from .quantities import QUANTITIES
from .registry import PromotionRefused, Registry
from .schema import ColumnSpec

__all__ = [
    "__version__",
    "Project",
    "Results",
    "ColumnSpec",
    "DataReport",
    "Issue",
    "check_data",
    "ForecastModel",
    "DriftReport",
    "InvalidInputData",
    "load_model",
    "LeakageError",
    "UnresolvedIssues",
    "PromotionPolicy",
    "check_gates",
    "Registry",
    "PromotionRefused",
    "train",
    "retrain",
    "reproduce",
    "QUANTITIES",
]


def quantities() -> str:
    """A readable list of the quantities you can declare, with units and ranges."""
    lines = []
    for q in QUANTITIES.values():
        units = ", ".join(q.units) if q.units else "any"
        lo, hi = q.plausible
        rng = f"{lo:g} to {hi:g} {q.canonical_unit}" if q.canonical_unit else "not checked"
        kind = "yes/no" if q.kind == "binary" else "numeric"
        lines.append(f"{q.name:26s} {kind:8s} units: {units:40s} plausible: {rng}")
    return "\n".join(lines)
