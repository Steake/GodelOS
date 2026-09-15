# V12 controller holdout diagnostic

Twenty deterministic replications, 96 feature cases each, three fixed policies. Zero provider calls. Cases are paired across policies. Seeds, sealed tasks and individual results accompany this report.

| Policy | Accuracy | Gain vs parent | Diagnostic passes |
|---|---:|---:|---:|
| parent | 75.0% | 0.0 points | 0/20 |
| blanket_repetition_penalty | 75.0% | 0.0 points | 0/20 |
| need_conditioned_penalty | 99.7% | 24.7 points | 20/20 |

## Interpretation

The blanket repetition penalty must be judged by family, not just its aggregate score. Escaping stale focus can come at the cost of suppressing recurring goals. These tests expose that tradeoff explicitly.

The need-conditioned comparator is an engineer-authored example, not an autonomously discovered improvement. Feature families and target labels encode our design assumptions. Fresh random instances do not establish independent task-family generalisation.

This is a controller diagnostic, not delayed cross-task LM transfer, a consciousness test, or evidence that the model modified its own inference machinery. All policies remain in shadow mode. Bootstrap intervals in each result resample independent feature cases, not language-model sessions.

Next: test recurring-goal recovery across actual interrupted episodes with independent task authorship and identity/content/ablated/no-state arms.
