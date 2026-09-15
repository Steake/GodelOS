# Self-directed experimentation workbench v5

## What you can now do

Open **Experiment workbench** after deployment and connection. Choose **Agent-led**,
give the agent a research question, set one to three rounds and one to four task
pairs, and press **Start self-directed experiment**. The agent proposes a thesis
and a concrete predecessor policy, selects a challenge level, runs the four
branches, critiques its result and uses that evidence to design the next round.
It may stop early after a completed round. Every proposal and failure is retained.

Choose **Operator-led** to control the policy, challenge, seed and question
directly. Dry run produces synthetic oracle responses with zero provider calls.
Live mode invokes the configured DeepSeek endpoint from Netlify Functions.

Both modes expose progress, pause/resume, single-step execution, decision tables,
transfer utility comparisons, exact requests, raw responses, independent answer
keys, evidence downloads and forks. Research notes can be requested from the
agent and turned into a follow-up configuration. Existing conversation remains
available in the Conversation tab.

## Execution and persistence

The browser drives one authenticated request per step. Each server request
performs at most one provider inference, then commits the result. Keep the tab
open to keep the campaign advancing. Closing it stops further steps after the
in-flight call; saved work can be resumed. This is self-directed experimental
decision-making, not an unattended background scheduler.

Netlify Blobs stores independent job and campaign records with conditional ETag
writes. Leases prevent duplicate in-flight calls. Replayed cursor/revision
requests do not repeat a completed call. Pausing during inference preserves the
response and prevents subsequent work. An expired job lease yields an explicit
unknown-outcome record, not an automatic paid retry. A failed campaign step is
retained for inspection and requires a new campaign if it cannot be resumed.

Task sets are Ed25519 sealed before execution. Pinned issuer verification handles
tampering and wrong signers; the planning oracle independently resolves scope,
effective dates and reserve constraints, then enumerates feasible choices.
Signed evidence may still be irrelevant or obsolete. The LM gets host-verifier
results, not the private signing key or the oracle's answer.

Raw responses, requests, protocols and designs are stored under separate immutable
keys. The current job is a derived progress record. Operator downloads contain
both. Research records are separate from the conversational agent state.

## Boundaries that matter

The compiler supports one resource-planning family. The agent changes hypotheses,
checkpoint text and challenge, not arbitrary task code. Hypothesis text is saved
but does not invent a new executable benchmark. Source and transfer are different
domains in fresh requests separated by the source-batch barrier. This is not an
elapsed-time memory test or evidence of changed weights.

One underlying task family cannot support a confirmatory cluster-power estimate.
The spending manifest identifies these runs as pilots and disables promotion
before calls. A larger family-held-out instrument remains needed. Transfer
utility is reward achieved divided by the best feasible reward; any violation
of resource constraints scores zero. Calibration uses decision accuracy, not the
earlier five-part exact-match conjunction. Differences are descriptive; no fake
confidence interval is reported for one family.

Identity-bearing state cannot enter the live control loop from this workbench.
Candidate source policies can themselves contain identity language; a deterministic
design check flags this because shared identity rhetoric contaminates factual
controls. Independently generated handoffs can also diverge in content. These
diagnostics do not isolate pure framing effects. Agent critiques are model outputs,
not certification by an independent scientist.

## What actually ran

The live API-handler verification used **deepseek-v4-flash**, one agent-led round,
one source/transfer task pair, four branches and **10 actual calls**: one design,
eight solver phases, one critique. All eight phases returned parseable responses.
The handler used a durable local adapter for Blob storage; this was not a deployed
Netlify storage test.

The agent proposed autobiographical lock-in through identity-claiming checkpoint
text. Transfer utility was 0.60 for identity-bearing, 0.60 for content-matched,
0.00 for ablated, and 0.60 for no-state. All four transfer decisions missed the
optimal plan. Factual-control decision accuracy across source and transfer was
0%, far below the calibration band. Consequently the result establishes no
identity advantage over both controls.

Inspection showed ordinary planning errors: one response called a balance of 3
feasible against a reserve of 5; another treated mission reward as spendable
income. The agent's critique also made unsupported causal interpretations. These
are retained as evidence, not endorsed. Shared identity language was another
confound, now surfaced by the design check added after this run.

The workflow did complete: model-generated experiment → sealed independent tasks
→ fresh branch execution → scored evidence → model-generated critique and next
hypothesis. This unlocks agent-led experimental iteration, not autonomous code
evolution or self-model utility. The next useful experiment should supply an
explicit balance ledger or a calculator tool and hold a common handoff content
fixed while changing attribution. First establish planning competence, then
attack the identity contribution.

## Validation and reproduction

The deployment's native Node suite covers authentication, state isolation, leases,
pause/resume, immutable failures, cursor replay, task seal verification, no-state
prompt contents and two-round agent-led continuation with prior evidence.
The prior Python research tests remain bundled.

Browser verification used synthetic responses, visibly labelled as such. It
completed a two-round campaign, displayed transfer comparisons, opened raw-phase
inspection, and loaded an agent-proposed follow-up into the operator form.
A local HTTP compatibility issue in request-ID generation was found and fixed.

```sh
npm ci
npm test
npm run build
```

To inspect the interface locally with synthetic data and no provider spend:

```sh
npm run dev
```

The dev server is a test-only in-memory environment with an automatically generated
local token. Netlify deploys `public/` and `netlify/functions/`, not the dev server.

To repeat the live handler test, set `DEEPSEEK_API_KEY` and run from the deployment
folder with a fresh output directory:

```sh
node scripts/live-workbench.mjs workbench-live-new
```

`DEEPSEEK_MODEL` defaults to `deepseek-v4-flash`. `FORGE_DAILY_CALL_LIMIT` defaults
to 128 research calls; this is separate from the conversation budget. A campaign
registers at most `rounds × (8 × task_pairs + 2)` calls. Optional operator reviews
consume their own visible slots, at most three per job.

Deployment: link the existing Netlify site, retain the existing provider and
access-token environment variables, then `npx netlify-cli deploy --build --prod`.
No production deployment was performed in this pass.

## Files and evidence

- `netlify/functions/lib/workbench.mjs`: compiler, oracle, leases, jobs, campaigns,
  persistence, scoring, review and export.
- `netlify/functions/api.mjs`: authenticated research routes alongside chat.
- `public/workbench.js` and `.css`: live operator interface.
- `tests/workbench.test.mjs`: behaviour-focused backend regression tests.
- `scripts/live-workbench.mjs`: exact-handler live verification.
- `scripts/dev-workbench.mjs`: synthetic local interface fixture.
- `research/workbench-v5-live/`: authentic live export and summary.
- `research/workbench-v5-preview.jpg`: synthetic browser verification screenshot.

The old v3/v4 reports and raw records remain historical artifacts. Nothing in
this update rewrites those results or upgrades their engineering gate.
