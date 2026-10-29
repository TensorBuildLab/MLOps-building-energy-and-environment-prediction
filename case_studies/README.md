# Case studies

| # | Case | Status |
|---|---|---|
| 00 | Synthetic messy office (`bemlops.datasets.messy_office`): one zone and AHU, 60 days, planted export problems | Done: see `examples/quickstart.py` |
| 01 | Reproduction of the 2024 study: DOE small office reference building, Tucson TMY3, EnergyPlus; estimate zone cooling rate from setpoint, zone temperature, outdoor temperature, solar radiation and occupancy (horizon 0) | Needs the original `input_fx.csv` / `output_fx.csv`, or a re-run of the EnergyPlus model |
| 02+ | Real buildings | To be decided: which buildings, which points, data permissions |

## For each real building

Each case study gets its own folder with:

- `README.md`: building type, size, climate, HVAC systems, metering, period
  covered, data access and permissions, and the prediction tasks
- `load.py`: reads the raw export from a local path (never committed) or
  downloads public data
- `run.py`: the tasks, using `bemlops`

## Public real-building datasets to consider

For results others can reproduce, alongside private campus data. Check each
dataset's license before use.

- LBNL Building 59 (Berkeley, CA): an office building with energy, indoor
  environment, HVAC and occupancy data
- Building Data Genome 2: about 3,000 meters from about 1,600 buildings

## Data policy

Raw building data is never committed to this repository (`data/` and
`runs/` are git-ignored). Building names can be anonymized in published
results if the owner asks.
