"""Command-line entry point, for schedulers and shell use.

    bemlops train     --config task.json --data trends.csv [--registry models --promote]
    bemlops predict   --registry models --name NAME --data latest.csv --out forecast.csv
    bemlops monitor   --registry models --name NAME --data last_two_weeks.csv
    bemlops retrain   --registry models --name NAME --data trends.csv
    bemlops reproduce --run runs/NAME-.../run.json --data trends.csv
    bemlops quantities

The configuration file is the JSON from ``Project.config()`` (also stored in every run.json).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def _read(path: str) -> pd.DataFrame:
    return pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)


def main(argv=None) -> int:
    from . import quantities
    from .pipeline import reproduce, retrain, train
    from .registry import Registry

    ap = argparse.ArgumentParser(prog="bemlops", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train")
    t.add_argument("--config", required=True)
    t.add_argument("--data", required=True)
    t.add_argument("--out", default="runs")
    t.add_argument("--registry")
    t.add_argument("--promote", action="store_true", help="promote if the gates pass")
    for name in ("predict", "monitor", "retrain"):
        s = sub.add_parser(name)
        s.add_argument("--registry", required=True)
        s.add_argument("--name", required=True)
        s.add_argument("--data", required=True)
        if name == "predict":
            s.add_argument("--out", required=True)
            s.add_argument("--warn", action="store_true", help="predict even if the live data fails checks")
        if name == "retrain":
            s.add_argument("--out", default="runs")
    r = sub.add_parser("reproduce")
    r.add_argument("--run", required=True)
    r.add_argument("--data", required=True)
    sub.add_parser("quantities")
    a = ap.parse_args(argv)

    if a.cmd == "quantities":
        print(quantities())
        return 0
    if a.cmd == "train":
        config = json.loads(Path(a.config).read_text(encoding="utf-8"))
        reg = Registry(a.registry) if a.registry else None
        out = train(_read(a.data), config, a.out, reg)
        print(out.project.results)
        print(f"Run saved to {out.run_folder}")
        if reg is not None:
            e = out.registry_entry
            print(f"Registered as version {e['version']} (gates passed: {e['gates_passed']})")
            if a.promote and e["gates_passed"]:
                reg.promote(out.project.name, e["version"], reason="Promoted from the command line.")
                print("Promoted to production.")
        return 0
    if a.cmd == "reproduce":
        res = reproduce(a.run, _read(a.data))
        print(json.dumps({k: v for k, v in res.items() if k in ("data_matches", "same_model", "metrics_match",
                                                                 "max_abs_difference")}, indent=2))
        return 0 if res["metrics_match"] and res["data_matches"] else 1
    reg = Registry(a.registry)
    data = _read(a.data)
    if a.cmd == "predict":
        model = reg.load(a.name)
        out = model.predict(data, on_error="warn" if a.warn else "raise")
        out.to_csv(a.out, index_label="time")
        print(f"Wrote {len(out)} rows to {a.out}")
        return 0
    if a.cmd == "monitor":
        rep = reg.load(a.name).check_drift(data)
        print(rep)
        return 2 if rep.retrain_recommended else 0
    if a.cmd == "retrain":
        print(json.dumps(retrain(data, reg, a.name, a.out), indent=2, default=str))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
