# Pilot deliverables (E5)

What each of the eight independent agents left in its task folder, so that the manual audit in
`../audit.csv` and the paper's pilot tables can be checked.

- Folder names: `T{task}_{condition}-{model}`. `A` = agent alone (bemlops forbidden), `C` = agent + bemlops.
- Included: every `.py`, `.json`, `.md`, `.txt` and `.log` file the agent wrote, plus the bemlops run
  records the `C` agents produced.
- Not included: `train.csv` (raw data; recreate it with `../make_tasks.py`), saved model files
  (`.joblib`), figures, and the hidden evaluation data.
- Absolute paths on the machine that ran the pilot are replaced by `<repo>`; nothing else was edited.
- The launch prompts are in `../PROMPTS.md`; the hidden-period scores are in `../results/`.

To re-score a deliverable: recreate the task folders with `make_tasks.py`, copy the agent's files
in, re-run its `train.py` (or equivalent) to rebuild the saved model, then run `../score.py`.
