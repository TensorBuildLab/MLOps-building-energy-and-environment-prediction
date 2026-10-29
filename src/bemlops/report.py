"""Write a run folder: human-readable report and model card, plus a complete machine-readable record.

    runs/<name>-<timestamp>/
        report.md             what was found, decided, and achieved
        model_card.md         what the model is for, how good it is, where it should not be trusted
        run.json              everything needed to audit, reproduce or re-check the run
        model.joblib          the deployable ForecastModel
        test_predictions.csv  actual vs predicted on the test period
        *.png                 plots (if matplotlib is installed)
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

import numpy as np
import pandas as pd

from ._version import __version__
from .governance import PromotionPolicy, check_gates

if TYPE_CHECKING:
    from .project import Project

METRIC_LABELS = {
    "rmse": "RMSE", "mae": "MAE", "cvrmse_pct": "CV(RMSE) %", "nmbe_pct": "NMBE %", "r2": "R²",
    "brier": "Brier score", "accuracy": "Accuracy", "balanced_accuracy": "Balanced accuracy", "f1": "F1",
    "roc_auc": "ROC AUC",
}
REGRESSION_KEYS = ["rmse", "mae", "cvrmse_pct", "nmbe_pct", "r2"]
CLASSIFICATION_KEYS = ["brier", "accuracy", "balanced_accuracy", "f1", "roc_auc"]


def fingerprint(df: pd.DataFrame) -> str:
    """Short hash of a table's contents, so a run can be tied to the exact data it used."""
    h = pd.util.hash_pandas_object(df, index=True).to_numpy()
    cols = "|".join(map(str, df.columns)).encode()
    return hashlib.sha256(h.tobytes() + cols).hexdigest()[:16]


def _git_commit() -> str:
    try:
        here = Path(__file__).resolve().parent
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=here, capture_output=True,
                             text=True, timeout=5)
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=here,
                               capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            return out.stdout.strip() + ("-dirty" if dirty.stdout.strip() else "")
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def environment() -> Dict[str, str]:
    import sklearn

    return {"bemlops": __version__, "code_commit": _git_commit(), "python": sys.version.split()[0],
            "numpy": np.__version__, "pandas": pd.__version__, "scikit-learn": sklearn.__version__,
            "platform": platform.platform()}


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (np.floating, float)):
        return None if not np.isfinite(obj) else float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (pd.Timestamp, pd.Timedelta, _dt.datetime)):
        return str(obj)
    if isinstance(obj, (str, int, bool)) or obj is None:
        return obj
    return str(obj)


def build_record(project: "Project", stamp: str) -> Dict[str, Any]:
    r, report = project.results, project.report_
    return _jsonable({
        "run": {"name": project.name, "created": stamp, "environment": environment()},
        "config": project.config(),
        "task": r.task,
        "data": {"raw_fingerprint": fingerprint(project.raw), "prepared_fingerprint": fingerprint(project.data),
                 "raw_rows": len(project.raw), "prepared_rows": len(project.data),
                 "summary": report.summary if report else {}},
        "data_check": report.to_dict() if report else None,
        "unresolved_errors": [i.id for i in project.unresolved()],
        "accepted_issues": project.accepted,
        "notes": project.notes,
        "prepare": {"options": project.prepare_options.to_dict() if project.prepare_options else None,
                    "log": project.prepare_log},
        "features": r.features,
        "split": r.split,
        "validation": r.validation.to_dict(orient="records"),
        "chosen_model": {"name": r.chosen, "params": r.chosen_params},
        "test": {"model": r.test, "baseline": {"name": r.baseline_name, **r.test_baseline}, "skill": r.skill,
                 "guideline14": r.guideline14},
        "warnings": r.warnings,
        "leakage_warnings": r.leakage_warnings,
        "event_log": project.log,
    })


def write_run(project: "Project", out_dir: Path) -> Path:
    r = project.results
    if r is None:
        raise RuntimeError("Nothing to save yet: run fit() first.")
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = out_dir / f"{project.name}-{stamp}"
    n = 1
    while folder.exists():
        n += 1
        folder = out_dir / f"{project.name}-{stamp}-{n}"
    folder.mkdir(parents=True)

    r.model.save(folder / "model.joblib")
    r.predictions.to_csv(folder / "test_predictions.csv", index_label="time")
    plots = _plots(r, folder, r.task.get("unit") or "")
    record = build_record(project, stamp)
    record["gates"] = check_gates(record, PromotionPolicy())
    (folder / "run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    (folder / "report.md").write_text(_markdown(project, plots), encoding="utf-8")
    (folder / "model_card.md").write_text(model_card(project, record), encoding="utf-8")
    return folder


# ----- plots -------------------------------------------------------------------
def _plots(results, folder: Path, unit: str) -> Dict[str, str]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return {}
    files = {}
    pred = results.predictions
    cls = results.task["task_type"] == "classification"
    col = "probability" if cls else "predicted"
    fig, ax = plt.subplots(figsize=(11, 3.6))
    window = pred.loc[: pred.index[0] + pd.Timedelta(days=7)]
    ax.plot(window.index, window["actual"], label="actual", lw=1.2)
    ax.plot(window.index, window[col], label=f"{col} ({results.chosen})", lw=1.0)
    ax.set_ylabel("probability / state" if cls else unit)
    ax.set_title("Test period (first week)")
    ax.legend(loc="upper right")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(folder / "test_timeseries.png", dpi=120)
    plt.close(fig)
    files["timeseries"] = "test_timeseries.png"

    if not cls:
        fig, ax = plt.subplots(figsize=(4.6, 4.4))
        ax.scatter(pred["actual"], pred["predicted"], s=4, alpha=0.4)
        lo = float(np.nanmin(pred[["actual", "predicted"]].to_numpy()))
        hi = float(np.nanmax(pred[["actual", "predicted"]].to_numpy()))
        ax.plot([lo, hi], [lo, hi], "k--", lw=1)
        ax.set_xlabel(f"actual ({unit})")
        ax.set_ylabel(f"predicted ({unit})")
        ax.set_title("Test period")
        fig.tight_layout()
        fig.savefig(folder / "test_scatter.png", dpi=120)
        plt.close(fig)
        files["scatter"] = "test_scatter.png"
    return files


# ----- markdown ----------------------------------------------------------------
def _metric_rows(model: Dict[str, float], base: Dict[str, float], keys: List[str], unit: str) -> List[str]:
    rows = []
    for k in keys:
        if k in model:
            label = METRIC_LABELS[k] + (f" ({unit})" if k in ("rmse", "mae") and unit else "")
            b = base.get(k, float("nan"))
            rows.append(f"| {label} | {model[k]:.3f} | {b:.3f} |")
    return rows


def _markdown(project: "Project", plots: Dict[str, str]) -> str:
    r, rep = project.results, project.report_
    unit = r.task.get("unit") or ""
    cls = r.task["task_type"] == "classification"
    keys = CLASSIFICATION_KEYS if cls else REGRESSION_KEYS
    out = [f"# Run report: {project.name}", "",
           f"**Task:** {r.task['description']}", "",
           "## Data check", ""]
    if rep is not None:
        s = rep.summary
        out.append(f"{s.get('rows')} raw rows from {s.get('start')} to {s.get('end')}, typical step {s.get('step')}.")
        out.append("")
        out.append(rep.to_markdown() if rep.issues else "No issues found.")
    if project.accepted:
        out += ["", "**Accepted as-is (with reasons):**", ""]
        out += [f"- `{k}`: {v}" for k, v in project.accepted.items()]
    if project.notes:
        out += ["", "**Decisions recorded:**", ""]
        out += [f"- {n}" for n in project.notes]
    out += ["", "## Preparation", ""]
    for e in project.prepare_log:
        col = f" `{e['column']}`" if e.get("column") else ""
        cnt = f" ({e['count']})" if e.get("count") is not None else ""
        out.append(f"- {e['step']}{col}: {e['detail']}{cnt}")
    out += ["", "## Split", "", "| Set | From | To | Rows |", "|---|---|---|---|"]
    for k in ("train", "val", "test"):
        a, b = r.split["bounds"][k]
        out.append(f"| {k} | {a} | {b} | {r.split['sizes'][k]} |")
    out.append(f"\nTime-ordered, with a {r.split['gap']} gap between sets.")
    out += ["", "## Validation", ""]
    cols = ["model", "type"] + [c for c in keys if c in r.validation]
    out.append("| " + " | ".join(METRIC_LABELS.get(c, c) for c in cols) + " |")
    out.append("|" + "---|" * len(cols))
    for _, row in r.validation[cols].iterrows():
        out.append("| " + " | ".join(f"{x:.3f}" if isinstance(x, float) else str(x) for x in row) + " |")
    out += ["", "## Test result", "", f"Chosen model: **{r.chosen}** {r.chosen_params or ''}", "",
            f"| Metric | Model | {r.baseline_name} |", "|---|---|---|"]
    out += _metric_rows(r.test, r.test_baseline, keys, unit)
    out.append(f"\nSkill vs {r.baseline_name}: **{r.skill:.2f}** (1 = perfect, 0 = no better than the baseline).")
    if r.guideline14:
        g = r.guideline14
        out.append(f"\nASHRAE Guideline 14 ({g['resolution']}): CV(RMSE) {g['cvrmse_pct']:.1f}% "
                   f"(limit {g['cvrmse_limit']:.0f}%), NMBE {g['nmbe_pct']:.1f}% (limit ±{g['nmbe_limit']:.0f}%): "
                   f"**{'passes' if g['passes'] else 'does not pass'}**.")
    for w in r.leakage_warnings + r.warnings:
        out.append(f"\n> Warning: {w}")
    if plots:
        out += ["", "## Plots", ""] + [f"![{k}]({f})" for k, f in plots.items()]
    out.append("")
    return "\n".join(out)


def model_card(project: "Project", record: Dict[str, Any]) -> str:
    """A short model card: intended use, data, performance, limitations, monitoring."""
    r = project.results
    unit = r.task.get("unit") or ""
    cls = r.task["task_type"] == "classification"
    keys = CLASSIFICATION_KEYS if cls else REGRESSION_KEYS
    tr0, tr1 = r.split["bounds"]["train"][0], r.split["bounds"]["val"][1]
    months_seen = sorted(set(pd.date_range(tr0, tr1, freq="D").month))
    missing_months = [m for m in range(1, 13) if m not in months_seen]
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    inputs = [f"`{k}` ({v.quantity}{', ' + v.unit if v.unit else ''}{', known ahead' if v.known_ahead else ''})"
              for k, v in project.specs.items() if k != project.target]
    lo, hi = r.model.target_range or (float("nan"), float("nan"))
    gates = record.get("gates", {})
    lines = [
        f"# Model card: {project.name}", "",
        "## Model", "",
        f"- **Task:** {r.task['description']}",
        f"- **Model:** {r.chosen} {r.chosen_params or ''}",
        f"- **Trained:** {r.model.trained_at} with bemlops {__version__} "
        f"(code {record['run']['environment']['code_commit']})",
        f"- **Data fingerprint:** raw `{record['data']['raw_fingerprint']}`, "
        f"prepared `{record['data']['prepared_fingerprint']}`", "",
        "## Intended use", "",
        project.intended_use or "Not stated. Add `intended_use=` to the Project.",
        "",
        "Valid only for this building and these inputs, at this time step and horizon.", "",
        "## Training data", "",
        f"- **Period:** {tr0} to {tr1} (train + validation)",
        f"- **Inputs:** {', '.join(inputs) if inputs else 'calendar only'}",
        f"- **Target range seen:** {lo:.3g} to {hi:.3g} {unit}" if not cls else
        f"- **Share of 'yes' in training:** {float(np.mean(project.data[project.target].dropna() >= 0.5)):.2f}",
        "",
        "## Performance (held-out test period, time-ordered)", "",
        f"Test period {r.split['bounds']['test'][0]} to {r.split['bounds']['test'][1]}.", "",
        f"| Metric | Model | {r.baseline_name} |", "|---|---|---|",
    ]
    lines += _metric_rows(r.test, r.test_baseline, keys, unit)
    lines += ["", f"Skill vs {r.baseline_name}: {r.skill:.2f}.", ""]
    if r.guideline14:
        lines.append(f"ASHRAE Guideline 14 (hourly): {'passes' if r.guideline14['passes'] else 'does not pass'}.")
        lines.append("")
    lines += ["## Promotion gates", "", "| Gate | Passed | Detail |", "|---|---|---|"]
    lines += [f"| {k} | {'yes' if v['passed'] else 'no'} | {v['detail']} |" for k, v in gates.items()]
    lines += ["", "## Limitations", ""]
    if missing_months:
        lines.append(f"- Months not seen in training: {', '.join(month_names[m - 1] for m in missing_months)}. "
                     f"Expect lower accuracy then; monitor closely.")
    lines.append("- Inputs outside the training range, sensor faults and operation changes (schedules, "
                 "setpoints, retrofits) reduce accuracy. `check_drift()` watches for all three.")
    for w in r.leakage_warnings + r.warnings:
        lines.append(f"- {w}")
    if project.accepted:
        lines.append("- Data issues accepted as-is: " + "; ".join(f"`{k}` ({v})" for k, v in project.accepted.items()))
    lines += ["", "## Monitoring", "",
              "Run `model.check_drift(recent_data)` regularly (e.g. weekly). Retrain when it recommends it; "
              "promote the new model only if it passes the gates and beats this one on the same recent data.", ""]
    return "\n".join(lines)
