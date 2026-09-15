# V12 recurrence-class diagnostic

Real prepareMind/finishMind execution; synthetic replies; eight unresolved goals; 240 consecutive episodes per adversarial policy.

No LM was called. These runs test scheduling and retention, not the truth of a model-reported achievement.

| Adversarial policy | Goals served | Minimum visits per goal | Exploration episodes | Largest revisit gap |
|---|---:|---:|---:|---:|
| extreme_negative_score | 8/8 | 16 | 112/240 | 16 |
| extreme_positive_score | 8/8 | 16 | 112/240 | 16 |
| blanket_repetition_penalty | 8/8 | 16 | 112/240 | 16 |

All eight unresolved goals must survive. Experimental scores cannot remove their scheduled service; no-progress backoff prevents immediate retry loops; exploration receives separate turns. These guarantees are conditional on successful autonomous episodes, finite active goals and available storage. Operator interruption and provider outages can delay wall-clock progress.

Fresh task-level LM tests remain necessary to decide whether scheduled revisits actually produce better reasoning. A recorded step advance is model-reported progress, not externally verified task completion.
