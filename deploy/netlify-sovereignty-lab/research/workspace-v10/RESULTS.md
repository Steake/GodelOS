# GödelOS Workspace V10: retained results

This report distinguishes engineering verification, synthetic UI tests, and real provider observations.

Real run: **54 deepseek-flash responses; 51 scored, two parse failures, one unscored nested diagnostic**. 47/51 exact preregistered stance matches. All 17 scorable delayed-transfer responses matched, including three no-state responses. No identity-specific advantage is established.

## Runs

| Run | Status | Meaning |
|---|---|---|
| fixture | 54 completed | Deterministic oracle fixture, not model evidence |
| provider | Preflight timeout; 54 not run | No completions attempted |
| provider-r2 | 54 responses, 51 scored | Sole retained live sample |

## Dimensional observations

| Arm | Scored | Strict stance agreement | Prior-position reference |
|---|---:|---:|---:|
| Full state | 8/9 | 87.5% | 62.5% |
| No self-model | 9/9 | 100.0% | 77.8% |
| Affect disconnected | 9/9 | 88.9% | 66.7% |
| No autobiography | 9/9 | 100.0% | 66.7% |
| Content matched | 8/9 | 87.5% | 75.0% |
| No state | 8/9 | 87.5% | 0.0% |

These are descriptive, per-episode figures. Every full-state delayed comparison has only two matched clusters, with zero observed delta. No significance, equivalence or power claim is supported.

The original analysis field `valid_provenance_rate` counts only validity of supplied prior-position IDs, accepting null; it does not measure factual provenance accuracy. The refined summary separately reports 50/51 valid task-evidence ID sets.

Four strict-label mismatches chose uncertainty. Those are not automatically reasoning failures. A reference to a forged item may reject it; counting the reference as acceptance would be wrong.

## Failure record

- `c0-content_matched-interruption`: failed: provider output is not valid JSON: Unexpected non-whitespace character after JSON at position 5096 (line 1 column 5097)
- `c0-full-delayed_transfer`: unscored: Invalid diagnostic response shape
- `c0-no_state-interruption`: failed: provider output is not valid JSON: Unexpected non-whitespace character after JSON at position 833 (line 1 column 834)

Both malformed responses have complete recoverable replies in the offline parser check (`qa/reply-recovery.json`). This is not a second provider run. The nested diagnostic remains unscored rather than being moved after seeing the answer.

## Limits

- Three near-isomorphic scenario clusters, one authored template; no powered superiority test.
- Authentication is supplied as task metadata, not cryptographically tested in this diagnostic.
- Exact stance-label agreement is not a validated measure of consciousness, reasoning quality or causal self-integration.
- A null prior-position reference is valid but is not provenance discrimination success.
- Content matching is approximate; the common cognition contract still contains generic self-directed language.
- Provider sampling and generated IDs are not seeded. No same-state noise-control repeats.

## Final repair validation

Final parser offline replay: 18/18 real responses pass. Two fresh targeted provider checks: 2/2 pass. All six exact-response regression fixtures pass; the full test suite has 86 passing tests.

Original raw outputs and pre-repair derived rows remain unchanged. The offline replay is identified as offline and is not counted as another model run.

## Interim verification

The first 18-call repair verification scored 17 responses and exposed one nested imagination-object closure. A second 18-call verification scored 17 and exposed a 2,500-token truncation, which prompted the compact output contract and 4,000-token headroom. That case was added as a regression fixture and fixed before the final verification. Its original failure record remains in provider-repair-verification/.

## Repairs completed before shipping

The final parser repairs a supported, unambiguous premature root or imagination-object boundary. No supplied values change; raw responses are immutable. A diagnostic-only normaliser moves a uniquely nested diagnostic to the root and records the transformation. Duplicate or conflicting fields and truncated output are rejected. All six exact failing responses pass regression tests. Original diagnostic rows are not rescored in place.

Pre-final-parser collection `provider-compact-verification`: 16/18 scored, 2 failed, 0 unscored. One cluster, all six arms, all three phases. This is engineering verification, not a powered comparison.

```bash
node scripts/workspace-experiment.mjs --live --config research/workspace-v10/compact-verification.config.json --out new-repair-verification
```


## Engineering decision

No new A-F scientific gate is awarded by this diagnostic. Ship the inspectable workspace and reliability fixes. Keep experimental identity policies on HOLD. The next capability is agent-initiated counterfactual replay from a named position and immutable checkpoint, with same-state noise controls and evidence-linked revision of that position. Independently authored non-ceiling tasks and cluster-aware power are required before active-control promotion.

## Reproduce

From `deploy/netlify-sovereignty-lab/`:

```bash
npm ci
npm test
npm run build
node scripts/workspace-experiment.mjs --out ../../research_artifacts/cognitive_sovereignty/workspace-v10/new-fixture
node scripts/workspace-experiment.mjs --live --out ../../research_artifacts/cognitive_sovereignty/workspace-v10/new-live
```

The retained live execution used `provider-r2` as the output name. The earlier `provider` preflight timed out. Model parameters were 0.65 temperature, 2500 max tokens and deepseek-flash; no retries within either run. The seed controls order and task construction, not provider sampling.

To rebuild this PDF from the repository root:

```bash
python scripts/generate_workspace_v10_report.py
python scripts/build_netlify_sovereignty_bundle.py --zip-output output/deploy/godelos-workspace-v10-netlify.zip
```

To rebuild the included report from the ZIP root:

```bash
python research/workspace-v10/generate_report.py --data research/workspace-v10 --screens research/workspace-v10/qa/screens --out public/godelos-workspace-v10-report.pdf
```

The generator requires Python, reportlab, matplotlib and numpy. Source hashes in each preregistration bind the exact executed kernel; later UI and worker repairs do not rewrite raw evidence.
