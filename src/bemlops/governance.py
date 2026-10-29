"""Promotion gates: the conditions a model must meet before it may go into production.

Gates are checked from the run record alone, so the same decision can be
re-checked later by anyone, without re-running the model.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass
class PromotionPolicy:
    min_skill: float = 0.05  # must beat the no-ML baseline by at least this much
    require_guideline14: bool = True  # energy-like targets with hourly or finer data must pass it
    allow_suspicious_inputs: bool = False  # inputs that look like copies of the target
    min_test_rows: int = 200

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def check_gates(record: Dict[str, Any], policy: PromotionPolicy = PromotionPolicy()) -> Dict[str, Dict[str, Any]]:
    """Evaluate each gate on a run record (the dict saved as run.json)."""
    test = record.get("test", {})
    gates: Dict[str, Dict[str, Any]] = {}

    blocking = record.get("unresolved_errors", [])
    gates["data_check_resolved"] = {"passed": not blocking,
                                    "detail": "all errors fixed or accepted with reasons" if not blocking
                                    else f"unresolved: {blocking}"}

    skill = test.get("skill")
    ok = skill is not None and skill >= policy.min_skill
    gates["beats_baseline"] = {"passed": bool(ok),
                               "detail": f"skill {skill:.3f} vs required {policy.min_skill}" if skill is not None
                               else "no skill recorded"}

    g14 = test.get("guideline14")
    if g14 is None or not policy.require_guideline14:
        gates["guideline14"] = {"passed": True, "detail": "not applicable"}
    else:
        gates["guideline14"] = {"passed": bool(g14.get("passes")),
                                "detail": f"CV(RMSE) {g14.get('cvrmse_pct'):.1f}%, NMBE {g14.get('nmbe_pct'):.1f}%"}

    suspicious = record.get("leakage_warnings", [])
    gates["no_suspicious_inputs"] = {"passed": policy.allow_suspicious_inputs or not suspicious,
                                     "detail": "none" if not suspicious else "; ".join(suspicious)}

    n_test = record.get("split", {}).get("sizes", {}).get("test", 0)
    gates["enough_test_data"] = {"passed": n_test >= policy.min_test_rows,
                                 "detail": f"{n_test} test rows (need {policy.min_test_rows})"}
    return gates


def gates_passed(gates: Dict[str, Dict[str, Any]]) -> bool:
    return all(g["passed"] for g in gates.values())
