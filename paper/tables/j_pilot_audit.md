| Task | Arm | Model | Planted faults found | Own causality test | Final model | Tokens (×10³) | Tool calls | Minutes |
|---|---|---|---|---|---|---|---|---|
| T1 | Alone | Opus | 7/8 | yes | Own: boosting on change from last value | 174 | 57 | 70 |
| T1 | Alone | Sonnet | 7/8 | yes | Own: extra trees + boosting on change | 228 | 136 | 57 |
| T1 | + framework | Opus | 7/8 | yes | Framework boosting on change + own lags | 265 | 97 | 152 |
| T1 | + framework | Sonnet | 7/8 | yes | Own: extra trees on change; framework for checks | 279 | 179 | 60 |
| T2 | Alone | Opus | 8/8 | yes | Own: boosting + meter-fault rules | 211 | 67 | 68 |
| T2 | Alone | Sonnet | 8/8 | no | Own: time-of-day profile + ridge + rules | 267 | 71 | 82 |
| T2 | + framework | Opus | 8/8 | yes | Framework random forest + own schedule inputs | 239 | 94 | 96 |
| T2 | + framework | Sonnet | 7/8 | yes | Own: profile + ridge; framework for checks | 281 | 134 | 68 |
