# Case studies

Real-building evaluation of `bemlops` on three public datasets, plus fault injection and an
eight-month lifecycle experiment. Every number in the paper comes from the files here.

| Folder | Data | What is run |
|---|---|---|
| `robod/` | ROBOD, 5 rooms of a university building in Singapore, 5-min data, Sep–Dec 2021 [Tekler et al. 2022] | 9 targets per room (CO2, temperature, humidity, PM2.5, people count, presence, a virtual people counter, chilled-water and plug energy): 45 tasks |
| `aalborg/` | Six office rooms and building systems in Aalborg, Denmark, 5-min data, Feb–Dec 2023 [Melgaard et al. 2024] | 27 tasks; fault injection (`faults.py`); lifecycle (`lifecycle.py`, `lifecycle_naive.py`) |
| `bdg2/` | Building Data Genome 2 [Miller et al. 2020] | Day-ahead hourly electricity for 20 buildings at 16 sites, one configuration for all |
| `lbnl_b59/` | LBNL Building 59 [Luo et al. 2022] | Not run: the repository does not allow scripted download (see its README) |

## Reproduce

```bash
python case_studies/download.py            # downloads and checksum-verifies the public data into data/raw/
python case_studies/run_all.py             # ROBOD, Aalborg, faults, lifecycle, BDG2 (hours; or name steps: run_all.py robod faults)
python case_studies/aalborg/lifecycle_naive.py   # the monthly-retrain arm of the lifecycle experiment
python case_studies/stats.py               # Diebold-Mariano tests, pilot statistics
python case_studies/make_results.py        # paper tables and figures
python case_studies/publish_records.py     # copy run records into */records/
```

Set `LOKY_MAX_CPU_COUNT` and `OMP_NUM_THREADS` to the number of cores you want to use.

## What is in each dataset folder

- `run.py`: the agent's work (loading, decoding, declarations, notes) followed by the tasks. The
  declarations and notes are frozen here and copied into every run record.
- `results/`: summary tables (`summary.csv`, `protocol_comparison.csv`, and for Aalborg the fault and
  lifecycle results).
- `records/`: the run record (`run.json`), report and model card behind every row of
  `summary.csv`. Test predictions, plots and saved models stay in the local `runs/` folder, because
  they contain the measured data; the scripts regenerate them.

## Corrections made during the study

ROBOD's chilled-water meters read exactly zero for whole days while the air-handling unit ran with
its cooling-coil valve open (9 days in Room 3, 1 in Room 4, 10 in Room 5). The independent pilot
agents found this; the first run of this case study did not. `robod/run.py` now sets those days to
missing (`mask_dead_chilled_water_meter`), and `robod/rerun_dead_meter.py` re-ran the three affected
tasks. The earlier rows are kept in `robod/results/*_before_dead_meter_mask.csv` and their records
in `robod/records/superseded/`.

## Data policy

Raw building data is never committed (`data/` and `runs/` are git-ignored). The datasets are
public under CC BY 4.0 (ROBOD, Aalborg) and CC BY-SA 4.0 (BDG2); only derived results are
published here.
