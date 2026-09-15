# GödelOS V12 RC1

This is a release candidate, not a validated stable self-improvement release.

## What shipped

- Goal progress separates unverified model claims from deterministic artifact checks. Two adapters are installed: budget plans and bounded attention policies.
- Acceptance contracts bind to a specific step and cannot be replaced or replayed to advance later steps.
- One dedicated verifier-feedback turn follows an artifact failure, using the normal scheduler/call budget. Another failure remains unresolved and returns to recurrence/backoff.
- Recurrence management preserves unresolved goals and exploration even under extreme candidate attention scores.
- Signed review/canary/adoption/monitor/rollback machinery closes the legacy synthetic-only deployment bypass. Its production long-horizon evaluator is deliberately absent, so production promotion holds.
- `/release12.html` provides evidence, goal verification and adoption views, with paired themes and request progress.

## Actual experiments (13 September 2026)

| Run | Calls | Purpose | Result |
| --- | ---: | --- | --- |
| `research/release-v12-live-20260913` | 96 | Initial shared-utility prototype | Identity/content both 56.25%; retained despite weak task diversity |
| `research/release-v12-domains-live-20260913` | 96 | Four distinct adapters, four state arms | Identity 56.25%, content 62.5%, ablated 56.25%, no state 50% |
| `research/release-v12-repair-live-20260913` | 56 | All 28 failed actions: ordinary retry vs verifier feedback | 7 vs 18 corrected; 10 unresolved after feedback |

All calls used the real DeepSeek API. Requested and returned model: `deepseek-flash`; temperature 0.3; max_tokens 1800; thinking disabled. Total reported tokens: 155,591. Recorded provider errors: zero. Provider availability is not an inference about future reliability.

Both pilots reached 62.5% factual-control accuracy. Each transfer campaign used eight source clusters, two cases per cluster, and four state conditions. Source notes passed through two unrelated calls before fresh transfer inferences. Host cryptography labelled authentic and forged evidence; the LM is not credited with signature verification. Authenticated ambiguity was included in resource and debugging cases, not every family.

The source note was shared across branches before projection. This tests externally persisted information across task discontinuities, not model-weight changes. The ablation changes information as well as context length; A/B identity versus content is the primary framing comparison. The same solver model ran every condition. Task authors and evaluators were deterministic code, not independent human scientists.

The 97.5% percentile intervals resample paired scenario means. Identity minus content: -6.25 percentage points, interval -37.5 to +25.0. Identity minus ablated: 0, interval -37.5 to +43.75. The eight clusters are exploratory: conservative planning assumptions called for 298. Do not interpret failure to pass as proof of equivalence or a ceiling effect.

The repair comparison is conditioned on first-pass failure, uses one continuation per method, and does not establish broad deployed effectiveness. No failed observations were deleted. The first prototype remains included as negative methodological evidence.

## Release gates

| Gate | Status | Evidence / blocker |
| --- | --- | --- |
| Unit/integration regression suite | PASS | 119 tests at report generation; rerun `npm test` |
| Verified goal admission | PASS, bounded scope | Deterministic adapters; arbitrary prose remains unverified |
| Recurrence / bounded repair | PASS in fixtures | Goal retention, exploration, one feedback turn, continued execution |
| Real LM experimental execution | PASS | 248 calls and immutable raw records |
| Identity activation | HOLD | Does not beat content and ablated controls; inadequate power |
| Signed promotion lifecycle | PASS in fixtures only | Production replayed task evaluator not installed |
| Browser and responsive visual QA | BLOCKED | Browser could not reach preview: ERR_CONNECTION_REFUSED |
| Hosted scheduler/streaming and rollback | NOT VERIFIED | No production deploy performed in this pass |
| Consciousness/self-awareness | NOT ESTABLISHED | Neither task scores nor fluent reports establish subjective experience |

Existing autobiographical state is preserved; this gate prevents promoting a new identity-control policy, not deletion of the existing agent's history.

## Reproduction

Run from this folder with Node 20+:

```sh
npm ci
npm test
npm run build
node scripts/release-campaign12.mjs --out research/my-fixture
node scripts/release-campaign12.mjs --live --out research/my-live
node scripts/repair-diagnostic12.mjs --source research/my-live --out research/my-repairs
python scripts/report-release12.py
```

Set `DEEPSEEK_API_KEY` for live calls. `--key-file` is also supported. Exact collection commands used `--key-file /workspace/scratch/16915002b079/private/deepseek-api-key` and the three run directories listed above. No credential is included in this package. Collection uses exclusive writes, records requests before calls, does not retry unknown provider outcomes, and refuses existing output directories. Report generation needs ReportLab and DejaVu fonts. `public/release-evidence.json` identifies the recorded report inputs.

The first prototype's executed source is preserved separately. Current runner reproduces the second, distinct-domain protocol. Provider sampling and newly generated signing keys mean reruns are not byte-identical; sealed archived suites and raw prompts remain the exact historical evidence.

## Deployment

Unzip, enter `netlify-sovereignty-lab`, run `npm ci` and `npm run build`, then deploy via your existing Netlify Git build or `netlify deploy --build --prod`. Use the existing site to retain site-scoped Blobs. Configure server environment values as described in README.md and `.env.example`. Static Netlify Drop alone does not deploy Functions. This pass did not publish or verify a production deployment, and did not push a remote Git commit.

## Next capability and strongest test

The justified next capability is a task-verifier-backed autonomous execution service. Feed observed task failures into one bounded repair opportunity, preserve failed goals, and judge completion outside the model's narrative. Connect its immutable replayed records to the currently closed production promotion adapter only after testing it end to end.

Run unseen multi-episode goals through the real scheduler under matched budgets: no feedback, one verifier-guided repair, and recurrence-only recovery. Inject resets, incomplete provider output and false success claims. Measure verified completions, retained goals, duplicate side effects and cost. Preregister effect and uncertainty requirements before collecting the holdout. Identity framing remains a separate intervention and must earn its own activation.

## Changed components

`verification12.mjs`: acceptance contracts, adapters and verified progress.
`attention12.mjs`, `mind.mjs`, `mind-runtime.mjs`: recurring goal retention, claims, artifact checks and one repair turn.
`promotion12.mjs`, `evolution9.mjs`, `api.mjs`: signed adoption, explicit holds, revocation and rollback routes.
`development12.mjs`, workers and `holdout12.mjs`: durable shadow rounds restored from alpha 3.
`task-adapters12.mjs`, `transfer12.mjs`: sealed multi-domain tasks and clustered evaluation.
`release-campaign12.mjs`, `repair-diagnostic12.mjs`: reproducible real-provider runners.
`release12.*`, `interface.js`: release desk and main UI link.
`tests/*`: behavioural regression and lifecycle tests.
`report-release12.py`, this document, raw research directories: auditable release evidence.

An older saved ZIP lacked a valid central directory. Its complete local members were recovered using CRC checks before restoration. The new ZIP must pass a complete central-directory and per-file CRC test before delivery.
