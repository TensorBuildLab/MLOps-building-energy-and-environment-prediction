"""Run every v3 experiment (ANALYSIS_PLAN_v3.md) with a fixed number of single-threaded workers, then merge.

    python case_studies/run_v3.py [workers]        (default 8; logs in runs/v3/logs/)
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
LOGS = REPO / "runs" / "v3" / "logs"
PY = sys.executable

JOBS = (
    [("e1_bdg2_%d" % i, ["case_studies/bdg2/run.py", f"{i}/4"]) for i in range(4)]
    + [("e1_robod_%d" % i, ["case_studies/robod/run.py", f"{i}/2"]) for i in range(2)]
    + [("e1_aalborg_%d" % i, ["case_studies/aalborg/run.py", f"{i}/2"]) for i in range(2)]
    + [("lc_bdg2_%d" % i, ["case_studies/bdg2/lifecycle_v3.py", "fit", f"{i}/8"]) for i in range(8)]
    + [("mv_bdg2_%d" % i, ["case_studies/bdg2/mv_v3.py", f"{i}/6"]) for i in range(6)]
    + [("protocol_%d" % i, ["case_studies/protocol_v3.py", f"{i}/6"]) for i in range(6)]
    + [("faults", ["case_studies/aalborg/faults.py"]),
       ("lc_aalborg", ["case_studies/aalborg/lifecycle.py"]),
       ("lc_aalborg_naive", ["case_studies/aalborg/lifecycle_naive.py"])]
)
AFTER = [
    ["case_studies/bdg2/run.py", "merge"],
    ["case_studies/robod/run.py", "merge"],
    ["case_studies/aalborg/run.py", "merge"],
    ["case_studies/bdg2/lifecycle_v3.py", "simulate"],
    ["case_studies/bdg2/mv_v3.py", "merge"],
    ["case_studies/protocol_v3.py", "merge"],
]


def env() -> dict:
    e = dict(os.environ)
    e.update({"LOKY_MAX_CPU_COUNT": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
              "MKL_NUM_THREADS": "1", "PYTHONIOENCODING": "utf-8", "PYTHONPATH": str(REPO / "src")})
    return e


def main(workers: int = 8) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    queue, running, t0 = list(JOBS), {}, time.time()
    while queue or running:
        while queue and len(running) < workers:
            name, args = queue.pop(0)
            log = open(LOGS / f"{name}.log", "w", encoding="utf-8")
            running[name] = (subprocess.Popen([PY, *args], cwd=REPO, env=env(), stdout=log, stderr=subprocess.STDOUT),
                             log, time.time())
            print(f"[{(time.time() - t0) / 60:6.1f} min] start {name}", flush=True)
        for name in list(running):
            proc, log, started = running[name]
            if proc.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:6.1f} min] done  {name} (exit {proc.returncode}, "
                      f"{(time.time() - started) / 60:.1f} min)", flush=True)
                del running[name]
        time.sleep(5)
    for args in AFTER:
        r = subprocess.run([PY, *args], cwd=REPO, env=env(), capture_output=True, text=True)
        print(" ".join(args[-2:]), "->", (r.stdout or r.stderr).strip().splitlines()[-1:] if (r.stdout or r.stderr) else "")
    print(f"all done in {(time.time() - t0) / 60:.0f} min")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
