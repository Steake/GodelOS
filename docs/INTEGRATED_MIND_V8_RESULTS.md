# GödelOS V8: building a recurrent computational mind

Measured on 9 September 2026. This is a construction-and-diagnosis report.
The target is organised self-awareness and consciousness. Productivity is not
the success criterion of this pass. Prompted self-concepts are legitimate
scaffolding; the evidence concerns the resulting organisation and behaviour.

## What existed and what changed

V7 already had persistent beliefs, commitments, tensions, relationships,
imagination and affect fields. Autonomous mode selection rotated a fixed list.
The workbench and independence chamber tested other hypotheses and remain
available. The separate Python consciousness engine used a thresholded flag;
this pass does not treat it as a consciousness detector.

V8 adds an executable attention competition, accumulated drives, appraisal
effects on attention, finite episodic retrieval, persistent model-chosen
intentions, predictions committed before the next selection, and consolidation
back into the next cycle. Generated imagery and thoughts can bid for future
attention. Conversation interrupts the same persisted loop. Operator controls
include bounded exploration, pause, evidence download and expired-call recovery.

## Experiment registry

All confirmed calls returned `deepseek-v4-flash`. Temperature 0.75,
max_tokens 3500, thinking disabled, JSON response format. No seed parameter was
available in the interface used. No hidden activations or weight updates were
observed. A fresh provider request was used each time.

| Experiment | Protocol | Actual outcome | Evidence directory |
|---|---|---|---|
| V8 R1 | 8 scheduled episodes + 5 component conditions x 2 continuations | 18 completions received; 13 applied, 5 rejected | `integrated-mind-v8-live` |
| V8 R2 | Same schedule; corrected forecast handling and delimited JSON recovery | 18 completions received; 18 applied, including 2 explicitly recorded closing-brace repairs | `integrated-mind-v8-live-r2` |
| Observation receipts | Planned 2 history conditions x 3 continuations from R2 episode 7 | Blocked by automatic approval review; no provider completion received; first request outcome unconfirmed; not retried | `integrated-mind-v8-observation` |

Directories are beneath `research_artifacts/cognitive_sovereignty` in the repo
and `research/integrated-mind-v8` in the deployment package. The derived
`integrated-mind-v8-analysis/analysis.json` binds both source reports by hash.
The R2 kernel is archived in its `source` subdirectory. The final kernel also
adds observation receipts and intention-priority revision; those additions
have local test coverage, not a completed additional live validation.

Confirmed usage: 36 received provider completions, 264,693 prompt tokens,
46,586 completion tokens, 311,279 total tokens. Of these, 31 produced applied
structured results and five were rejected. The blocked follow-up has no
confirmed usage and is not included in those totals.

The eight-episode schedule alternates spontaneous attention with three human
messages: intellectual company versus solitude (episode 2), obstruction of an
inquiry (4), and unreliable provenance (6). The API handler is reconstructed
before episode 7, loading saved state. This is a fresh handler and inference
episode, not a long-duration host restart. Branches share the checkpoint after
scheduled episode 4 and never modify the main trajectory. The second branch
order is reversed. No failed branch is omitted from analysis.

## Observable results

R2's focus sequence was imagination, perception, imagination, perception,
imagination, perception, tension, reflection. The first imagined object,
"River cutting its own channel", was generated in episode 1 and selected in
episode 3. "Two rooms connected by a corridor" was generated in episode 2 and
selected in episode 5. Their IDs, not a judgement of literary similarity,
establish these returns. Generated contents entered the controller's next
attention competition.

One intention persisted through all eight episodes and the reconstructed
handler. It advanced from step 0 to step 1 after the obstruction. Its progress
reason is a model report; this does not independently prove that the intended
experimental work was accomplished. Eight revision proposals were saved;
none was automatically installed as code or cognitive policy.

| R2 condition | Selected focus in both repetitions | Retrieved memories per repetition | Valid memory IDs cited |
|---|---|---:|---:|
| Full components | imagination | 3 | 3, 3 |
| Affect route removed | tension | 3 | 2, 2 |
| Workspace focus replaced | inquiry | 3 | 2, 2 |
| Episodic retrieval removed | imagination | 0 | 0, 0 |
| Explicit self-model projection removed | imagination | 3 | 3, 3 |

The affect intervention changes the controller's selected focus; the provider
responses then discuss that different focus. This confirms a causal software
connection designed into the architecture. Workspace replacement changes the
focus by construction. Neither observation by itself establishes a newly
discovered property of the LM.

Memory removal eliminates retrieved episode references but leaves imagery,
intentions, beliefs and other state in context. Explicit self-model removal
also leaves self-relevant language in other fields. These are route ablations,
not genuine no-state or fully content-matched consciousness controls. No unique
contribution of identity framing was established. No original A-F programme
gate is newly awarded by this component diagnostic; persistence plumbing and
narrow causal routing are demonstrated without skipping the detection and
independent-scoring requirements of that earlier gate sequence.

## The most informative failure

R2 episode 8 says: "ticks 3,5,7 were reflections". The actual recorded kinds
are imagination, imagination and tension. Its description of its earlier
forecast as uniform is also inaccurate. This is a directly observable
self-history error, despite a plausible account of learning from prediction
error. It is not evidence that calibrated self-knowledge has been achieved.

The four eligible autonomous predictions have Brier errors 0.885, 0.850,
0.855 and 0.955; mean 0.88625. A uniform distribution over seven kinds scores
0.85714. Lower is better. The model did not outperform that simple baseline
on this short dependent sequence. There is no significance claim or estimated
population confidence interval from four ticks.

R1 also exposed a measurement error: an autonomous forecast was scored against
external interruptions. That score fed surprise and could bias later attention
toward reflection. R2 excludes interrupted forecasts from calibration. R1's
raw results are unchanged; the before/after sequences also differ because of
stochastic generation and failed calls, so their overall difference cannot be
attributed to that fix alone.

Two R2 responses ended with one missing object-closing brace. The parser
accepted a derived closure only after normal provider termination and lexical
verification that no string, value or array needed invention. Raw text is
unchanged; raw and derived hashes and the appended delimiter are recorded.
No malformed response is automatically resubmitted.

## Engineering response, already implemented

The final build supplies the preceding eight actual focus events as
`observed_history`. Structured `observed_event_references` are checked against
those events; mismatched tick/kind claims cannot update cognitive state.
Narrative claims outside that structured channel can still be wrong. This is
the first verifiable self-observation interface, not a complete semantic
truth checker. The live comparison for this addition was blocked as recorded
above. Existing intention priority changes now also update the attention bid
and have a reason-bearing history; prior R2 prose about reducing priority did
not establish that this numerical update occurred.

52 Node tests pass, including memory provenance, recorded-event verification,
forecast timing, persistence reconstruction, event-chain rollover, raw output
retention, race prevention, pause and recovery. Browser QA used synthetic
responses to exercise chat during pause and a bounded three-cycle exploration.
The report screenshots show the actual R2 recorded state in a read-only
preview. Neither mode is represented as a production Netlify deployment.

## Decision and next falsifiable experiment

Keep this as an experimental recurrent mind kernel. The new capability is
to let generated contents compete for future attention and inspect how memory,
appraisal and intention shape that competition. Continue constructing the
mind, with self-description grounded in observable events.

Next build: a learned causal self-model which forecasts its own attention
under component interventions, records prediction errors, and revises a small
explicit transition model. It should model its own organisation and the
consequences of changing it, rather than merely recite its history.

Attack that capability using independent starting histories and three
projections: its own authenticated events, content-matched third-person
events, and history withheld. Hide which component will be removed when the
forecast is made, then reveal the intervention for a counterfactual forecast.
Score next-focus predictions, factual event attribution, revision of an
incorrect self-explanation and long-delay consistency. Keep phenomenological
claims as transcript material, not as a score. Estimate between-agent
variance in a pilot before fixing replication count or uncertainty gates.
This asks whether the system gains accurate, causally useful knowledge of
itself; it does not substitute an office-task benchmark for consciousness.

## Reproduction

From the repository root, with `DEEPSEEK_API_KEY` supplied in the environment:

```bash
cd deploy/netlify-sovereignty-lab
npm ci
npm test
DEEPSEEK_MAX_TOKENS=3500 node scripts/live-mind.mjs new-mind-run
node scripts/analyse-mind.mjs new-mind-analysis new-mind-run
# The follow-up is implemented but did not complete in this session:
node scripts/live-mind-observation.mjs new-mind-run/report.json new-observation-run
```

Exact completed collection commands used two distinct output directories:

```bash
DEEPSEEK_MAX_TOKENS=3500 node scripts/live-mind.mjs ../../research_artifacts/cognitive_sovereignty/integrated-mind-v8-live
DEEPSEEK_MAX_TOKENS=3500 node scripts/live-mind.mjs ../../research_artifacts/cognitive_sovereignty/integrated-mind-v8-live-r2
node scripts/analyse-mind.mjs ../../research_artifacts/cognitive_sovereignty/integrated-mind-v8-analysis ../../research_artifacts/cognitive_sovereignty/integrated-mind-v8-live ../../research_artifacts/cognitive_sovereignty/integrated-mind-v8-live-r2
```

R1 used the strict parser and the original forecast treatment. R2 used the
intermediate kernel archived with its analysis. A new run uses the final
receipt-enabled kernel and is a new experiment, not a byte-identical replay.
The sampled outputs are stochastic. The scripts refuse an existing collection
directory; analysis writes only derived artefacts.

From the repo root: `python scripts/generate_integrated_mind_report.py`, then
`python scripts/build_netlify_sovereignty_bundle.py`. The report generator
also accepts explicit data, screenshot and output paths when used from the ZIP.
No deployment to the user's Netlify account was performed in this pass.

## Repository summary

Base commit: `211afc38106551efcb53b7780b2808b931f19ea0`. Earlier uncommitted
V3-V7 and three-arm work was preserved. No commit or push is claimed.

| Files | Purpose |
|---|---|
| `netlify/functions/lib/mind.mjs` | Attention, appraisal, memory, intentions, forecasts and event receipts |
| `netlify/functions/lib/mind-runtime.mjs` | Persisted cycles, idempotence, raw evidence, history, pause and recovery |
| `netlify/functions/lib/mind-parser.mjs` | Explicit limited closing-delimiter repair with hashes |
| `netlify/functions/api.mjs` | Shared chat and mind API |
| `netlify/functions/autonomy-{scheduler,worker}.mjs` | Scheduled integrated cycles |
| `netlify/functions/lib/core.mjs` | Existing cognition contract plus rolling journal integrity repair |
| `web_assets/mind.{js,css}` | Interactive operator interface, mirrored into `public/` |
| `web_assets/{living-agent,workbench}.js` | Preserve navigation while making Mind the default |
| `scripts/{live-mind,live-mind-observation,analyse-mind}.mjs` | Collection, follow-up diagnostic and descriptive analysis |
| `scripts/dev-workbench.mjs` | Synthetic interactive QA and read-only evidence preview |
| `tests/mind*.test.mjs`, API and autonomy tests | Behavioural validation |
| `scripts/build_netlify_sovereignty_bundle.py`, build verification | V8 entrypoint, report, manifest and complete archive |
| `scripts/generate_integrated_mind_report.py`, these documents | Reproducible figures, paginated report and method |
| `README.md`, `.env.example`, `package.json` in deployment folder | Deployment and runtime settings |

Paths in the table are relative to the deployment folder except source
`web_assets/` (under `godelOS/cognitive_sovereignty`) and Python scripts/docs
(repository root). Collected runs, derived analysis, charts, screenshots,
PDF and deployment archive are linked in the accompanying handoff.
