# Case studies

Real-building evaluation of `bemlops` on three public datasets. Every number in the paper comes from the
files here. The experiments follow a pre-specified analysis plan, [`ANALYSIS_PLAN_v3.md`](ANALYSIS_PLAN_v3.md),
committed together with the frozen package version (0.3.1, fingerprint `84f7e16c74ac9fdc`) before any of
them was run.

| Folder | Data | What is run |
|---|---|---|
| `bdg2/` | Building Data Genome 2 [Miller et al. 2020], cleaned meters, 2016–2017, hourly | Day-ahead electricity for 200 pre-specified buildings at 16 sites (`run.py`); M&V pseudo-savings, 2016 baseline and 2017 reporting period (`mv_v3.py`); a year of retraining policies with a gate audit for 50 buildings (`lifecycle_v3.py`) |
| `robod/` | ROBOD, 5 rooms of a university building in Singapore, 5-min data, Sep–Dec 2021 [Tekler et al. 2022] | 9 targets per room (CO2, temperature, humidity, PM2.5, people count, presence, a virtual people counter, chilled-water and plug energy): 45 tasks |
| `aalborg/` | Six office rooms and building systems in Aalborg, Denmark, 5-min data, Feb–Dec 2023 [Melgaard et al. 2024] | 27 tasks; fault injection (`faults.py`); lifecycle case (`lifecycle.py`, `lifecycle_naive.py`) |
| `protocol_v3.py` | ROBOD Rooms 4–5, Aalborg Room A and systems, first 40 BDG2 buildings | Shuffled, blocked and forward-chaining evaluation of the same model on the same rows; feature selection on all rows vs in each fold |
| `lbnl_b59/` | LBNL Building 59 [Luo et al. 2022] | Not run: the repository does not allow scripted download (see its README) |

## Reproduce

```bash
python case_studies/download.py            # downloads and checksum-verifies the public data into data/raw/
python case_studies/run_v3.py 8            # every v3 experiment with 8 workers (about 2 h), then the merges
python case_studies/analysis_v3.py         # statistics, paper tables and figures, results_v3/key_numbers.csv
python case_studies/publish_records.py     # copy run records into */records/
```

`run_v3.py` sets single-threaded numerical libraries per worker and puts `src/` first on the Python path, so
the runs use the package in this checkout.

## Outputs

- `*/results/summary.csv`: one row per task of the portfolio experiment (E1).
- `results_v3/`: M&V (`mv.csv`), protocol (`protocol.csv`), lifecycle (`lifecycle_bdg2.csv`,
  `gate_audit_bdg2.csv`, `lifecycle_aalborg/`), faults (`faults/`), Diebold–Mariano tests (`dm_tests.csv`),
  every task with its statistics (`tasks_v3.csv`), meters with week-long zero stretches
  (`bdg2_zero_stretches.csv`) and `key_numbers.csv`, from which the paper's numbers are traced.
- `*/records/`: the run record (`run.json`), report and model card behind every row of `summary.csv`. Test
  predictions, plots and saved models stay in the local `runs/` folder, because they contain the measured
  data; the scripts regenerate them.
- `*/results_v2/`, `*/records_v2/`: the earlier version of the study (package 0.2.0.dev0), kept for
  comparison.

## Data faults found in the public data

- ROBOD's chilled-water meters read exactly zero for whole days while the air-handling unit ran with its
  cooling-coil valve open (9 days in Room 3, 1 in Room 4, 10 in Room 5). `robod/run.py` sets those days to
  missing (`mask_dead_chilled_water_meter`).
- In BDG2, the cleaned hourly meters of the Gator site change value only at midnight (daily totals spread over
  24 h); the stuck check flags and masks them. The meters of the Lamb site read zero or close to it for weeks
  to months in 2017; no check flags this, because zero is a valid reading for an idle meter.

## Data policy

Raw building data is never committed (`data/` and `runs/` are git-ignored). The datasets are
public under CC BY 4.0 (ROBOD, Aalborg) and CC BY-SA 4.0 (BDG2); only derived results are
published here.
