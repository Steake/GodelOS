# V10 change map

The working tree already contained V3-V9 experiments and interface changes.
This pass preserves them and changes the separate Netlify workspace. No blanket
Git reset, unrelated architecture rewrite or production deployment was made.

| File or group | Purpose |
|---|---|
| `godelOS/cognitive_sovereignty/web_assets/workspace10.css` | Shared light/dark tokens, readable legacy cards and selected controls, responsive columns. |
| `web_assets/workspace10.js` | Live input graphic, attention bids, memory/stance trace, revision ledger, worker status and recovery. |
| `web_assets/mind.js` | Draft retention, queued/failed-message visibility, snapshot refresh, scroll preservation. |
| `netlify/functions/lib/core.mjs` | Before/after stance history and third-person/fresh-state context framing. |
| `lib/mind.mjs` | V10 migration, actual-current-event validation, interventions before attention selection, trace breakdown. |
| `lib/interventions.mjs` | Six explicit context/state manipulations, including genuine no-state preparation. |
| `lib/mind-runtime.mjs` | Serial message handling, retained attempts, latency, readable reply recovery and quarantined invalid updates. |
| `lib/mind-parser.mjs` | Bounded value-preserving syntax repair, raw/derived hashes, complete-reply extraction. |
| `lib/autonomy-control.mjs`, `autonomy-worker.mjs`, `autonomy-scheduler.mjs` | Persisted status, nonce-aware recovery, quota refund, contention deferral, dispatch receipts. |
| `netlify/functions/api.mjs` | Model provenance, worker status/recovery routes and current provider default. |
| `lib/workspace-diagnostic.mjs` | Conditions, sealed task bank, compact output contract, scoring, schema normalisation and paired descriptions. |
| `scripts/workspace-experiment.mjs` | Immutable collection, preflight, raw prompts/responses, exact executed source and derived analysis. |
| `scripts/replay-output-regressions.mjs`, `verify-output-contract.mjs` | Reproducible offline repairs and fresh provider interface verification. |
| `tests/workspace10.test.mjs`, `tests/mind-parser.test.mjs`, `tests/autonomy.test.mjs`, `tests/fixtures/` | Behavioural regressions, six actual malformed responses, migration, interventions and background scheduling. |
| `scripts/dev-workbench.mjs` | Synthetic UI preview and a 390px responsive frame; never a production authentication route. |
| `scripts/build_netlify_sovereignty_bundle.py` | Cache-busted V10 entrypoint, report/evidence copying, manifest and complete Netlify source ZIP. |
| `scripts/verify-build.mjs`, package files, `.env.example`, README | Build verification, current version and deployment instructions. |
| `scripts/generate_workspace_v10_report.py` | Nine-page illustrated report and derived figures, with explicit layout bounds. |

Paths beginning `lib/`, `netlify/`, `tests/` or deployment `scripts/` refer to
`deploy/netlify-sovereignty-lab/`. Canonical `web_assets/` means
`godelOS/cognitive_sovereignty/web_assets/`. Generated `public/` copies are built
from canonical assets and included in the ZIP.

## Evidence layout

- `fixture/`: 54 deterministic instrument episodes, not LM evidence.
- `provider/`: timed-out preflight, no completions.
- `provider-r2/`: original 54 real responses, 51 scored.
- `provider-repair-verification/`: 18 responses, 17 initially scored; nested closure found.
- `provider-repair-final/`: 18 responses, 17 initially scored; truncation found.
- `provider-compact-verification/`: 18 responses, 16 initially scored; final string/trailing-brace repairs added.
- `final-output-check/`: two fresh provider calls, both passed without repairs.
- `qa/final-parser-replay.json`: all 18 compact-run outputs pass the final parser offline.
- `qa/repaired-output-replay.json`: six exact-response repair fixtures, zero provider calls.
- `qa/tests.txt`, `qa/browser-checks.json`, `qa/screens/`: test log and explicitly synthetic UI verification.
- `evaluation-summary.json`, `RESULTS.md`, `figures/`: derived results. No original run was rescored in place.

The task bank remains too easy and too small to establish identity-specific
transfer benefit. The fixes repair execution and observability; they do not turn
the diagnostic into a consciousness measurement or a powered promotion test.
