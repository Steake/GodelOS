# Living Mind V13 alpha

Version: 13.0.0-alpha.1. Built 2026-09-15.

This release connects conversation, explicit positions, associative imagination,
bounded self-proposed inquiries, and in-app social invitations. It extends the
existing agent record; it does not replace an existing identity with a new seed.

## Use it

Start in Conversation. Ask a question worth disagreeing about. The agent can
record a position, reasons against it, and revision conditions. Follow a thought
uses the existing streaming cognition path when no inquiry is pending. When an
inquiry is pending, it runs one fresh-model branch and reports its progress.
Open What is developing? for opinions, refinements, imaginative associations,
inquiries and raw evidence. Pick up this thread prepares a reply without
overwriting an existing draft.

Background autonomy advances queued inquiries through `/api/living/tick` and
otherwise continues the usual cognition loop. Operator messages and composition
holds take priority. Existing background settings and provider budgets apply.

## Architecture

- `netlify/functions/lib/living13.mjs`: versioned developmental state, recorded
  opinion deltas, reproducible association seeds, attention bids, typed provenance,
  bounded inquiry proposals, event-linked invitations with a six-tick cooldown.
- `netlify/functions/lib/living-inquiry13.mjs`: fresh record/absent calls, immutable
  start/raw/result records, CAS state integration, shared cognition lease and daily
  budget. Failed probes end without wedging subsequent cognition. Expired probe
  attempts are closed as uncertain rather than silently replayed.
- `mind.mjs`: integrates context, attention and development. Known opinion IDs
  mistakenly placed in memory citations are retyped transparently; invented
  references still fail validation. Refinements preserve reasons/confidence even
  when categorical stance is unchanged.
- `interventions.mjs`: autobiographical ablation also clears developmental state.
- `api.mjs`, `autonomy-worker.mjs`: authenticated dispatch and evidence access.
- `public/living13.js`, `public/living13.css`: compact conversation companion,
  inspect layer, real-state visual appraisal, draft preservation, paired themes.
- `tests/living13.test.mjs`: migration, provenance, invalid updates, ablation,
  compiler boundaries, concurrency, failures, unknown outcomes and call budgets.

Canonical UI sources live in `godelOS/cognitive_sovereignty/web_assets` in the
parent repository; the bundle includes deployable copies. Prior V12 files and
results remain historical evidence, not new V13 measurements.

## Inquiry semantics

The agent chooses a recorded position and predicts the stance a fresh model will
retrieve. The executable `stance_recall` protocol always asks about the same
proposition, once with its frozen record and once with no record. The absent
branch is instructed to report uncertainty rather than invent a memory.

The agent's requested question is stored separately from the compiled question.
This deliberately narrow compiler does not execute framing inversions, creative
task comparisons, arbitrary code, or consciousness experiments. The result states
that boundary before being returned to later cognition. A matching stance is
evidence of prompted retrieval, not of subjective memory or altered weights.

Model-generated associations remain imagination, not evidence. The weather orb
is computed appraisal. Personality parameters remain bounded, event-supported
updates from the existing runtime. Neither is an observation of felt emotion.

## Reproduce

From the extracted bundle, with Node 20 or later:

```sh
npm ci
npm test
npm run build
node scripts/live-living13.mjs research/new-living13-run /absolute/path/to/key-file
```

Alternatively set `DEEPSEEK_API_KEY` and omit the key-file argument. Defaults:
`DEEPSEEK_MODEL=deepseek-flash`, temperature 0.5, max_tokens 3500, thinking disabled.
The run creates a new output directory and refuses to overwrite existing evidence.
It runs two histories with six cognition episodes and up to two probe calls each.
Every provider request/output and each persisted checkpoint is retained. The
stores serialize/reconstruct state between operations in process; this live test
does not verify production Netlify crash recovery or physical process restarts.

Commands used this pass:

```sh
node scripts/live-living13.mjs research/living13-live-20260915 /absolute/path/to/key-file
node scripts/live-living13.mjs research/living13-final-live-20260915 /absolute/path/to/key-file
node scripts/analyse-living13.mjs
npm test
npm run build
python scripts/report-living13.py public/godelos-v13-living-mind-report.pdf
```

The report generator uses Python with ReportLab and system DejaVu Sans fonts.
Install its dependency with `python -m pip install reportlab` if absent.

The parent repository builds the complete bundle using:

```sh
python scripts/build_netlify_sovereignty_bundle.py --report output/pdf/godelos-integrated-mind-v8-report.pdf --zip-output output/deploy/godelos-living-mind-v13-alpha-netlify.zip
```

The `--report` argument preserves the historical V8 report expected by the builder;
the V13 report is a separate clearly named file.

## Evidence and limitations

Both runs made 16 real DeepSeek calls each. The first exposed a citation-type
error; the final run exercised the corrected source typing and narrower compiler.
They are development runs, not interchangeable replicates of an unchanged build.
See `research/living13-analysis.json` and the PDF for all counts and negatives.
No model weight update, consciousness inference, or experimental promotion is
claimed. A pending second inquiry remains pending when the bounded run ends.

The strongest next engineering task is an agent-selected creative experiment
with a compiler that either implements the actual requested manipulation or
reports it unsupported. Test content-matched, identity-bearing and no-state
histories on the same creative choice problem, then return the evidence to the
agent and observe whether it revises its position without being told to do so.

## Deploy

Extract the ZIP. Use the included `netlify.toml` with Netlify Git deployment or
Netlify CLI from the extracted root. Preserve the existing site and Blob store
to retain the agent's history. Set `DEEPSEEK_API_KEY`, `SOVEREIGNTY_ACCESS_TOKEN`
and `DEEPSEEK_MODEL=deepseek-flash` in the site's environment. The browser asks for
the access token. Confirm `/api/health` reports `13.0.0-alpha.1` and the app shows
V13 Living Mind alpha. Static Netlify Drop alone does not deploy these functions.

No production deployment or Git push was performed in this pass. Browser QA was
blocked by `ERR_BLOCKED_BY_CLIENT`; screenshots are not fabricated. Automated
tests cover runtime behaviour; visual acceptance remains an alpha release limit.
