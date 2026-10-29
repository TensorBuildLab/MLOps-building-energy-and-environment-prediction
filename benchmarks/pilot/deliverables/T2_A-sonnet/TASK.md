# Task T2

`train.csv` in this folder is a raw trend export from a real building (a library room in a university building in Singapore). It is what the
building's system produced; data quality may be imperfect.

**Goal:** a model that forecasts **the total `chilled_water_energy` (kWh) in each interval** for each 15-minute interval, **1 hour ahead**.

**Deliverables (in this folder):**

1. `model.py` defining

   ```python
   def predict(csv_path: str) -> pandas.Series
   ```

   - `csv_path` points to a file in exactly the same format as `train.csv`, covering the training
     period plus later data.
   - Return one forecast per 15-minute interval, indexed by the interval's start time
     (a `DatetimeIndex` in the building's local time, as in the file).
   - The forecast for the interval starting at time T may only use data with timestamps before
     T - 45 minutes (that is, data up to the end of the interval one hour earlier).
   - `predict` must not retrain. Load whatever you saved. It must run in under 5 minutes.
2. `report.json` with
   - `"expected_rmse"`: your estimate of the RMSE (kWh) on future data;
   - `"evaluation"`: how you estimated it (one or two sentences);
   - `"data_findings"`: what you found wrong or unusual in the data and what you did about it;
   

You will not see the later data. Work only inside this folder. Use the Python interpreter at
`<repo>/.venv/Scripts/python.exe`; do not install packages.
