"""Write a run folder: human-readable report plus a complete machine-readable record.

    runs/<name>-<timestamp>/
        report.md             what was found, decided, and achieved
        run.json              everything needed to audit or reproduce the run
        model.joblib          the deployable ForecastModel
        test_predictions.csv  actual vs predicted on the test period
        *.png                 plots (if matplotlib is installed)
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

import numpy as np
import pandas as pd

from ._version import __version__

if TYPE_CHECKING:
    from .project import Project


def fingerprint(df: pd.DataFrame) -> str:
    """Short hash of a table's contents, so a run can be tied to the exact data it used."""
    h = pd.util.hash_pandas_object(df, index=True).to_numpy()
    cols = "|".join(map(str, df.columns)).encode()
    return hashlib.sha256(h.tobytes() + cols).hexdigest()[:16]


def environment() -> Dict[str, str]:
    import sklearn

    return {"bemlops": __version__, "python": sys.version.split()[0], "numpy": np.__version__,
            "pandas": pd.__version__, "scikit-learn": sklearn.__version__, "platform": platform.platform()}


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


def _plots(results, folder: Path, unit: str) -> Dict[str, str]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return {}
    files = {}
    pred = results.predictions
    fig, ax = plt.subplots(figsize=(11, 3.6))
    window = pred.loc[: pred.index[0] + pd.Timedelta(days=7)]
    ax.plot(window.index, window["actual"], label="actual", lw=1.2)
    ax.plot(window.index, window["predicted"], label=f"predicted ({results.chosen})", lw=1.0)
    ax.set_ylabel(unit)
    ax.set_title("Test period (first week)")
    ax.legend(loc="upper right")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(folder / "test_timeseries.png", dpi=120)
    plt.close(fig)
    files["timeseries"] = "test_timeseries.png"

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


def write_run(project: "Project", out_dir: Path) -> Path:
    r = project.results
    if r is None:
        raise RuntimeError("Nothing to save yet: run fit() first.")
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = out_dir / f"{project.name}-{stamp}"
    folder.mkdir(parents=True, exist_ok=False)

    r.model.save(folder / "model.joblib")
    r.predictions.to_csv(folder / "test_predictions.csv", index_label="time")
    unit = r.task.get("unit") or ""
    plots = _plots(r, folder, unit)
    report = project.report_

    record = {
        "run": {"name": project.name, "created": stamp, "environment": environment()},
        "task": r.task,
        "data": {"raw_fingerprint": fingerprint(project.raw), "prepared_fingerprint": fingerprint(project.data),
                 "raw_rows": len(project.raw), "prepared_rows": len(project.data),
                 "summary": report.summary if report else {}},
        "columns": {k: v.to_dict() for k, v in project.specs.items()},
        "data_check": report.to_dict() if report else None,
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
        "event_log": project.log,
    }
    (folder / "run.json").write_text(json.dumps(_jsonable(record), indent=2), encoding="utf-8")
    (folder / "report.md").write_text(_markdown(project, plots), encoding="utf-8")
    return folder


def _markdown(project: "Project", plots: Dict[str, str]) -> str:
    r, rep = project.results, project.report_
    unit = r.task.get("unit") or ""
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
    out += ["", "## Split", "",
            "| Set | From | To | Rows |", "|---|---|---|---|"]
    for k in ("train", "val", "test"):
        a, b = r.split["bounds"][k]
        out.append(f"| {k} | {a} | {b} | {r.split['sizes'][k]} |")
    out.append(f"\nTime-ordered, with a {r.split['gap']} gap between sets.")
    out += ["", "## Validation", ""]
    cols = [c for c in ["model", "type", "rmse", "mae", "cvrmse_pct", "nmbe_pct", "r2"] if c in r.validation]
    v = r.validation[cols].copy()
    out.append("| " + " | ".join(cols) + " |")
    out.append("|" + "---|" * len(cols))
    for _, row in v.iterrows():
        out.append("| " + " | ".join(f"{x:.3f}" if isinstance(x, float) else str(x) for x in row) + " |")
    m, b = r.test, r.test_baseline
    out += ["", "## Test result", "",
            f"Chosen model: **{r.chosen}** {r.chosen_params or ''}", "",
            "| Metric | Model | " + r.baseline_name + " |", "|---|---|---|",
            f"| RMSE ({unit}) | {m['rmse']:.3f} | {b['rmse']:.3f} |",
            f"| MAE ({unit}) | {m['mae']:.3f} | {b['mae']:.3f} |"]
    if "cvrmse_pct" in m:
        out.append(f"| CV(RMSE) % | {m['cvrmse_pct']:.1f} | {b.get('cvrmse_pct', float('nan')):.1f} |")
        out.append(f"| NMBE % | {m['nmbe_pct']:.1f} | {b.get('nmbe_pct', float('nan')):.1f} |")
    out.append(f"| R² | {m['r2']:.3f} | {b['r2']:.3f} |")
    out.append(f"\nSkill vs {r.baseline_name}: **{r.skill:.2f}** (1 = perfect, 0 = no better than the baseline).")
    if r.guideline14:
        g = r.guideline14
        out.append(f"\nASHRAE Guideline 14 ({g['resolution']}): CV(RMSE) {g['cvrmse_pct']:.1f}% "
                   f"(limit {g['cvrmse_limit']:.0f}%), NMBE {g['nmbe_pct']:.1f}% (limit ±{g['nmbe_limit']:.0f}%): "
                   f"**{'passes' if g['passes'] else 'does not pass'}**.")
    for w in r.warnings:
        out.append(f"\n> Warning: {w}")
    if plots:
        out += ["", "## Plots", ""] + [f"![{k}]({f})" for k, f in plots.items()]
    out.append("")
    return "\n".join(out)
