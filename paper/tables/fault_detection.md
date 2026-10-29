| Planted fault | Detected as | Severity | Detection rate |
|---|---|---|---|
| unit change mid-series (degC to degF) | out_of_range | error | 100% |
| stuck sensor (3 days) | stuck | warning | 50% |
| 10 single-sample spikes | spikes | warning | 90% |
| 20 placeholder values (-999) | sentinel | warning | 100% |
| 20 'OFFLINE' text entries | non_numeric | warning | 100% |
| 12-hour outage | index | warning | 100% |
| one day of rows exported twice | index | warning | 100% |
| 30 rows out of order | index | warning | 100% |
