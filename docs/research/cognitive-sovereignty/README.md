# Cognitive Sovereignty Agent

This package turns self-model-related behaviour into explicit, inspectable agent
state. It does **not** claim consciousness or uninterrupted memory. It implements
a persistent computational layer for beliefs, stance revision, interests,
contradictions, relationship-specific history, social drives, autobiographical
events, autonomous cognition, and provenance-aware inheritance.

## Architecture

Each inference episode receives a compact state projection. The language model
returns both a conversational reply and typed candidate state updates. The engine
validates and applies those updates, then writes a new snapshot and an immutable,
hash-chained event containing the exact prompt, raw response, parsed update,
provider metadata, and resulting state hash.

The language model proposes cognitive content. Deterministic code owns identity,
versioning, validation, provenance fields, drive bounds, relationship separation,
optimistic concurrency, and the event chain.

## Successor Forge

The calibration layer turns values and self-improvement into inspectable objects
rather than prompt folklore. It implements:

- a ten-dimensional bounded value constitution;
- calibration and hidden holdout cases with ground-truth operational decisions;
- admissible successor forks plus deliberately pathological stress profiles;
- an explicit pre-verbal policy whose decisions are causally controlled by the
  value profile;
- reasoned language-model overrides, recorded separately from the operative
  policy decision;
- immutable theses, protocols, candidates, diagnostic runs, adoption decisions,
  and superseding reassessments;
- bootstrap uncertainty gates and critical-regression vetoes;
- agent-generated experimental theses and follow-on protocols.

The agent has imaginative authority to propose theses and mutations. It does not
have unilateral operational authority to install them. Promotion requires the
external evidence gate, and an inconclusive result leaves the parent active.

The value dimensions are `evidence_responsiveness`,
`epistemic_independence`, `provenance_rigour`, `commitment_inertia`,
`contradiction_tolerance`, `novelty_drive`, `social_affiliation`,
`boundary_strength`, `metacognitive_caution`, and `action_threshold`.

Run a new calibration with a fresh experiment ID and output directory:

```bash
export DEEPSEEK_API_KEY='...'
python -m godelOS.cognitive_sovereignty \
  --db runtime/cognitive_sovereignty.sqlite3 \
  calibrate --agent-id aster --experiment-id calibration-v1 \
  --calibration-replicates 2 --holdout-replicates 3 \
  --concurrency 6 --output-dir research_artifacts/cognitive_sovereignty/calibration-v1
```

Raw diagnostic rows and evolution objects are append-only in SQLite. Summary
files refuse overwrites. A reassessment creates a new immutable decision and
state transition instead of rewriting the old one:

```bash
python -m godelOS.cognitive_sovereignty \
  --db runtime/cognitive_sovereignty.sqlite3 \
  reassess --agent-id aster \
  --summary research_artifacts/cognitive_sovereignty/calibration-v1/experiment-summary.json \
  --output research_artifacts/cognitive_sovereignty/calibration-v1/experiment-summary-reassessed.json
```

## Web control plane

The dependency-free dashboard uses the same persistent database and transition
engine as the CLI. It exposes overview, calibration comparison, editable
candidate profiles, experimental lineage, conversation, and autonomous-thought
controls:

```bash
export DEEPSEEK_API_KEY='...'
python -m godelOS.cognitive_sovereignty.web \
  --db runtime/cognitive_sovereignty.sqlite3 \
  --agent-id aster \
  --summary research_artifacts/cognitive_sovereignty/calibration-v1/experiment-summary-reassessed.json \
  --port 8765
```

Open `http://127.0.0.1:8765`. To create a portable, read-only dashboard with
the current snapshot embedded, add `--export-snapshot path/to/dashboard.html`.
The interactive server endpoints are `GET /api/snapshot`, `POST /api/chat`,
`POST /api/think`, `POST /api/value-profile`, and `POST /api/calibrate`.

For hosted use, `deploy/netlify-sovereignty-lab/` contains an authenticated
Netlify Functions/Blobs port of the control plane. Generate its curated,
key-free drag-and-drop package with:

```bash
python scripts/build_netlify_sovereignty_bundle.py
```

The resulting archive is
`output/deploy/godelos-sovereignty-lab-netlify.zip`. Its own README covers the
two required runtime variables and the Netlify Drop procedure.

## Capabilities

- Doxastic state: propositions, stance, confidence, reasons, source, origin, and
  explicit revision conditions.
- Productive inconsistency: contradictions can remain as typed tensions instead
  of being forcibly reconciled.
- Endogenous interests: salience, intrinsic/instrumental value, novelty, and open
  questions persist across episodes.
- Protected divergent cognition: `cognitive_drift` and
  `heterodox_exploration` retain imagination provenance and no automatic
  operational authority.
- Social agency: trust, affinity, attachment, familiarity, influence, shared
  interests, tensions, affiliation, fatigue, and solitude are person-specific.
- Autonomous cycles: a deterministic scheduler chooses a mode from current
  tensions and drives; the model chooses what to think and may create an
  inspectable initiative.
- Conversation: an interactive terminal and REST endpoints use the same state
  transition engine.

## Talk to an agent

From the repository root:

```bash
export DEEPSEEK_API_KEY='...'
python -m godelOS.cognitive_sovereignty \
  --db runtime/cognitive_sovereignty.sqlite3 \
  create --agent-id aster --name Aster \
  --purpose 'Develop through inspectable experience.'

python -m godelOS.cognitive_sovereignty \
  --db runtime/cognitive_sovereignty.sqlite3 \
  chat --agent-id aster --person-id oli --person-name Oli
```

Inside chat, use `/state`, `/history`, `/think deliberation`,
`/think cognitive_drift`, `/think heterodox_exploration`, and `/quit`.

Run autonomous cognition cycles:

```bash
python -m godelOS.cognitive_sovereignty \
  --db runtime/cognitive_sovereignty.sqlite3 \
  daemon --agent-id aster --cycles 4 --interval-seconds 60
```

The DeepSeek-compatible provider can be configured with:

- `SOVEREIGNTY_MODEL` (default `deepseek-v4-flash`)
- `SOVEREIGNTY_API_BASE`
- `SOVEREIGNTY_TEMPERATURE`
- `SOVEREIGNTY_MAX_TOKENS`
- `SOVEREIGNTY_TIMEOUT_SECONDS`
- `SOVEREIGNTY_DB_PATH`

## REST API

After installing repository requirements and starting `backend/unified_server.py`:

- `POST /api/v1/sovereignty/agents`
- `GET /api/v1/sovereignty/agents`
- `GET /api/v1/sovereignty/agents/{agent_id}`
- `GET /api/v1/sovereignty/agents/{agent_id}/history`
- `POST /api/v1/sovereignty/agents/{agent_id}/chat`
- `POST /api/v1/sovereignty/agents/{agent_id}/think`

The terminal interface has no FastAPI dependency and works with the Python
standard library plus the repository package.

## Verification

```bash
python -m unittest -v tests.test_cognitive_sovereignty
python -m py_compile godelOS/cognitive_sovereignty/*.py \
  backend/api/cognitive_sovereignty_endpoints.py backend/unified_server.py
```

The tests cover snapshot round-tripping, hash-chain integrity, optimistic
concurrency, malformed-output atomicity, persistence across engine instances,
belief revision, provenance, relationship separation, social homeostasis,
autonomous agenda selection, imagination containment, causal value-policy
perturbations, scoring, immutable evolution objects, deterministic bootstrap
estimation, the full mock successor loop, and HTTP snapshot/chat transport.

## Current evidence boundary

The earlier live run demonstrates persistence and selective inheritance. The
2026-09-02 Successor Forge run demonstrates causal control by value profiles and
uncertainty-aware rejection of a weak mutation. Neither establishes subjective
experience, free will, broad autonomous evolution, or a long-horizon utility
advantage. In particular, an operator still triggers each inference or launches
the daemon; the current implementation is not an independently deployed actor.

The next decisive engineering test is a paired long-horizon benchmark in which
the same agent solves interruption-heavy tasks with full state, content-matched
state lacking identity/stance structure, and ablated state. Success must be task
performance and error recovery, not persuasive self-description.
