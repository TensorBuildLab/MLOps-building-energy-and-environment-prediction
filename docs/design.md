# Design

## The split: judgment vs guarantees

Building data is too varied for a fixed pipeline, and too easy to get wrong
for free-form code alone. `bemlops` splits the work:

- **Judgment** (agent or engineer, in their own code): reading any export
  format, decoding point names, deciding what a fault means for this
  building, choosing the target, horizon and time step, designing extra features.
- **Guarantees** (the package, the same every time): units checked against
  physics, time-ordered evaluation, no leakage, honest baselines, standard
  metrics, a complete record.

The package accepts any pandas table, so it never limits what the agent can
do. It checks the result.

## Guardrails and why

| Guardrail | Why |
|---|---|
| Every used column must be declared with a quantity and unit | Point names are ambiguous; a declaration can be checked, a guess cannot. |
| Declarations are checked against plausible physical ranges, and the likely unit is named | Wrong units are the most common silent error in BAS data (degF vs degC, fraction vs %, W vs kW). |
| Errors block `fit()` until fixed or accepted with a written reason | Problems must be decided on, not ignored; the reason goes into the record. |
| No random split exists in the package | Shuffled time series let a model see the neighbours of every test hour, which inflates accuracy. The 2024 study had this problem. |
| Gap of `horizon` steps between train, validation and test | No forecast is ever evaluated with a model trained on data later than the forecast time. |
| Inputs are lagged by at least the horizon unless declared `known_ahead` | A live model cannot see measured values from the future. |
| Feature selection and tuning use the training set only | Selecting features on the full data leaks test information (another 2024 issue). |
| Input gaps are forward-filled only; the target is never filled | Interpolation uses future values; filled targets invent answers. |
| Cleaning decisions (spikes, stuck stretches) use only earlier readings | Otherwise later data decides what earlier data looked like, and live serving cannot reproduce training. Found by the pilot agents and the code review. |
| Interval totals with missing readings become missing | A total over an incomplete interval is too small; using it would fill missing targets with zeros. |
| Decimal commas and unreadable timestamps stop the project | Guessing turns "21,5" into 21 and swaps day and month without a trace. |
| Skill is measured against the strongest no-ML baseline: persistence, same time yesterday, or the time-of-day profile | Accuracy numbers mean little without a no-skill reference, and a weak reference flatters a model; for scheduled loads, persistence is weak. |
| A rolling-origin backtest is reported next to the single test period | One unusual test period (a holiday, a schedule change) should not decide the verdict alone. |
| A 90% prediction interval, with its coverage checked on the test period | Operators need a range, and a range is only useful if it is honest. |
| Guideline 14 for energy-like targets, MAE in physical units for indoor environment | CV(RMSE) divides by the mean, which makes temperature errors look tiny. |
| Every run writes data fingerprints, decisions, settings, versions and results | Industry use needs an audit trail; research needs reproducibility. |
| Acceptances made on earlier data never approve errors on new data | Accepting "column RH missing" must not silently cover "OAT and RH missing" in an automated retrain. |

## Definitions

**Forecast with horizon h steps**: the prediction for interval *T* uses
data from intervals up to *T − h* only. Resampled values are labelled by the
start of their interval, so with *h ≥ 1* every input interval is complete
before the target interval begins.

**Estimation (horizon 0)**: a virtual sensor. The target is estimated from
other inputs measured at the same moment, and is never an input itself.

**Skill**: `1 − RMSE_model / RMSE_baseline`. 1 is perfect, 0 is no better
than the baseline, below 0 is worse.

## What is deliberately not in the package

- Loaders for specific BAS vendors' export formats: there are too many, and an
  agent writes a loader in seconds. The skill has a playbook instead.
- Automatic guessing of point meanings: that is judgment, and it belongs where
  it can be questioned. The package checks the guess.
- An MCP server: it can be added later as a thin layer over the same API.
