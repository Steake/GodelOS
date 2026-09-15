# V12 alpha 3 — recurrence management and durable development

This is the first implemented V12 slice, not a completed general self-improving agent.
It replaces browser-dependent three-round controller evolution with durable,
bounded, server-driven shadow experiments. Existing chat, streaming, cognitive
state, and manual controller interfaces remain available.

## Operator flow

Open Research → **V12 alpha · Development chamber** → **Start 3 background rounds**.
The first round is dispatched immediately. Subsequent rounds are dispatched by
the production Netlify scheduler every 15 minutes, including with the page closed.
Progress, completed attempts, failures, and review findings are displayed in the
chamber. Pause development prevents subsequent rounds; an in-flight result is
retained. The global thinking pause also prevents new development calls.

Existing Netlify environment: `DEEPSEEK_API_KEY`, `SOVEREIGNTY_ACCESS_TOKEN`,
and Netlify's `URL`. No new secret is needed. Deploy the full project with its
Functions, not just `public/` via static drag-and-drop. Scheduled execution needs
a production deploy; it does not run automatically in a local preview.
See [background functions](https://docs.netlify.com/build/functions/background-functions/)
and [scheduled functions](https://docs.netlify.com/build/functions/scheduled-functions/).

## What executes

1. Persist a run manifest with a 1–10 round budget (UI default 3).
2. Reserve a round using a conditional-write lease and run/round delivery identity.
3. Ask the configured LM to generate a thesis, bounded attention-expression AST,
   and authored tests. Give it previous round outcomes and critical reviews.
4. Compile the AST without arbitrary JavaScript execution; run authored tests and
   the existing 80-case synthetic suite; create the existing signed package.
   Before candidate generation, seal 96 fresh controller cases using a new random
   seed. After generation, compare the candidate with its recorded parent on those
   same cases. Keep seeds, oracles and cases out of the candidate prompt.
5. Apply a deterministic independent review of reused controls, missing transfer,
   uncertainty, and ceiling effects. This reviewer is not an independent LM.
6. Save an immutable round outcome before advancing the cursor. Carry the result
   into the next development prompt, without rewriting the live autobiography.

The existing daily limit of 10 evolution design calls is shared with manual
candidate design. Failed and unknown attempts consume rounds. An expired lease
does not replay the uncertain provider call. A late response cannot overwrite a
recorded round outcome. Duplicate deliveries cannot consume the next round.
An evidence-write/cursor-write gap is reconciled from the immutable outcome.

## Why no automatic adoption yet

The 80-case suite is reused and exposed through successive results. Its bootstrap
interval describes that synthetic sample, not held-out generalisation. V12 therefore
records **shadow only** even when the legacy gate passes. Existing explicit manual
deployment remains an attention-only operator action under the legacy gate.
Neither route modifies model weights, arbitrary code, or the agent's constitution.

Next implementation: independently sealed tasks with competing recurring goals,
interruption recovery and delayed transfer; identity-bearing, content-matched,
ablated and genuine no-state arms; cluster-aware preregistered promotion thresholds.
Only fresh transfer evidence should unlock automatic live-controller adoption.

## API and records

All routes require the existing bearer access token:

- `GET /api/development/status`
- `GET /api/development/evidence` exports the current run manifest, round outcomes,
  sealed cases, controller results and referenced signed packages. This operator
  endpoint is authenticated and is never inserted into generation prompts.
- `POST /api/development/start` with `{"rounds":3}`
- `POST /api/development/pause` with `{}`
- `POST /api/development/resume` with `{}` to continue the same paused run
- `POST /api/development/advance` with `{}` for explicit local diagnostic execution
- Background delivery uses `{run_id, expected_round}` to reject stale duplicates.

Blob records: `development/v12/current`, immutable
`development/v12/runs/<id>/manifest` and `.../rounds/<number>`.
Packages, raw completions, design prompts and failures use the existing
`evolution/v9/` records; round summaries reference signed package IDs.

## Validation in this pass

The automated fixture suite exercises compiler → signing → review → next-round
context with synthetic LM responses, plus concurrency, duplicate delivery, pause,
provider failure, expired leases, late responses, and cursor-gap recovery.
No live DeepSeek experiment or production scheduling verification is claimed.
An unauthenticated reachability request to the DeepSeek API timed out after 15
seconds during alpha 2; no provider request with credentials was sent.
The preview server starts, but the remote browser could not reach it in this
environment; visual and click-through verification is incomplete.
Historical PDFs bundled with this release remain historical V8/V10 reports,
not V12 evidence.

From the repository root:

```sh
cd deploy/netlify-sovereignty-lab
node --test tests/*.test.mjs
cd ../..
python scripts/build_netlify_sovereignty_bundle.py --report output/pdf/godelos-integrated-mind-v8-report.pdf --zip-output output/deploy/godelos-workspace-v12-alpha-netlify.zip
cd deploy/netlify-sovereignty-lab
node scripts/verify-build.mjs
```

## Changed surfaces

- `lib/development12.mjs`: durable state machine and deterministic reviewer.
- `lib/evolution9.mjs`: optional prior-development context for thesis generation.
- `api.mjs`: authenticated development endpoints and release identity.
- `development-worker-background.mjs`, `development-scheduler.mjs`: asynchronous execution.
- `interface.js`: start, pause, progress and review inspection; manual tools retained.
- `tests/development12.test.mjs`: fault and end-to-end fixture tests.
- Builder, package metadata, version badge and verifier: V12 alpha identity.

This advances experiment continuity and inspectability. It does not establish
consciousness, intrinsic motivation, improved agent utility, or autonomous learning.

## Alpha 2 executed diagnostic

Command from `deploy/netlify-sovereignty-lab`:

```sh
node scripts/run-holdout12.mjs research/development-v12-holdout
```

For reproduction choose a new output directory; the runner refuses to overwrite
an existing experiment. Twenty seeded replications × 96 feature cases × three
fixed, engineer-authored policies = 5,760 controller decisions, zero LM calls.
Results and raw cases are in `research/development-v12-holdout/` in this bundle.

| Controller | Overall accuracy | Escape stale focus | Protect recurring goal |
|---|---:|---:|---:|
| Parent | 75.0% | 0% | 100% |
| Blanket repetition penalty | 75.0% | 100% | 0% |
| Need-conditioned penalty | 99.7% | 99.0% | 100% |

The old winning intervention exchanges one failure for another. A more selective
penalty illustrates an implementable alternative, but is engineer-authored and
near ceiling on these deliberately narrow feature families. This is not evidence
of autonomous discovery. The parent's 75% is controller-label accuracy, not an LM
factual-control pilot. Fresh instances do not make the known task families unseen.

Reviews now show fresh paired gains and intervals and explicitly block family
regressions. Automatic promotion remains disabled: identity/content/ablated/no-state
transfer experiments, independent LM task authorship, power planning and production
verification are still needed. The holdout does not silently stand in for them.

## Alpha 3: solve recurrence as a scheduling class

The alpha 2 coefficient experiment exposed conflation of repetition with uselessness.
The fix is an explicit service policy around the score, not another fitted penalty.
It is active in the hand-engineered attention controller. Model-generated candidate
policies still remain in shadow mode and cannot alter the service policy.

- **Separate goal service from exploratory scoring.** Every second successful idle
  episode offers a goal-service slot. Among eligible goals, least recently served
  wins before score. Other slots prefer eligible exploration. Empty lanes can yield
  to the other lane. Human messages always take priority.
- **Back off failed approaches, not commitments.** No recorded step progress causes
  a 2/4/8/16 idle-episode cooldown, capped at 16. Repeated stalls return as a replanning
  focus. Blocked goals remain recorded and periodically revisited.
- **Reset for a state change, not new rhetoric.** Recorded step advancement resets
  stalls. Rephrased justifications and priority changes do not. Similar exploratory
  titles share cooldown across IDs using a lexical heuristic. Distinct goal IDs are
  never merged by that heuristic.
- **Wake with scoped evidence.** Authenticated `POST /api/mind/intention/evidence`
  accepts `{intention_id,evidence}`. A changed evidence digest makes that goal
  eligible again. Repeating identical evidence is a no-op. This is explicitly
  operator-supplied evidence, not automatically authenticated truth. It does not
  silently mark the goal completed or the blocker resolved.
- **Preserve obligations.** Active and blocked intentions are not removed by
  history truncation. Sixty active intentions is the admission limit for new goals;
  older migrated active intentions are preserved. Completed history is bounded
  separately. New-goal overflow is quarantined rather than evicting an active goal.
- **Make selection inspectable.** Each bid carries eligibility, stall count, due
  idle episode, last service and reason. Selection traces identify scheduled goal
  service versus competitive exploration. Service state survives resets and is
  removed by the appropriate experimental ablations.

Mind schema migrates additively from 8/10 to 12. It retains existing intentions,
memories and personality. Experimental `repeats` input remains bounded 0–8, but
now describes stagnant visits rather than every recurrence indiscriminately.
Historical experiments used the previous controller and must not be pooled with
new experiments as if that intervention had not changed.

Reproduction, from the deployment directory:

```sh
node --test tests/attention12.test.mjs tests/mind.test.mjs
node scripts/run-recurrence12.mjs research/development-v12-recurrence-reproduction
```

The shipped final diagnostic is `research/development-v12-recurrence-final/`.
The earlier run is preserved separately. Each executes 720 real controller episodes
using synthetic replies, not a live LM: eight unresolved goals, three adversarial
score policies, 240 episodes each. Additional tests cover progress, changed evidence,
renamed duplicate topics, human interruption, serialization and retention limits.

Limits: fairness is over successful idle episodes, not elapsed time during outages
or continuous operator contact. A model-reported step is not independently verified
task success. Lexical similarity is an imperfect duplicate detector; evidence
relevance still needs judgement. This architecture prevents scoring-based starvation
and silent goal eviction; it does not prove that every scheduled revisit is useful.
