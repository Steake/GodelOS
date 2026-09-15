# Integrated Mind V8: architecture and execution contract

## Audit before modification

The deployed path is `deploy/netlify-sovereignty-lab`: `api.mjs` loads one
versioned agent record from Netlify Blobs, `core.mjs` projects state into a model
prompt and applies structured updates, and the autonomy scheduler dispatches a
background worker. V7 rotated a hard-coded list of cognition modes. The living
agent UI exposes conversation, interests, beliefs, affect and autobiography.
The independent experimental chambers and prior evidence remain separate.

The Python `backend/core/unified_consciousness_engine.py` also implements a
GlobalWorkspace, driven partly by a phi-like input and a coalition threshold
that sets a `conscious` flag. That threshold is not empirical evidence of
consciousness. This build preserves that interface but does not import its
classification into the deployed agent. No unrelated backend rewrite occurs.

## Design hypothesis

Deliberately scaffold a persistent computational self: shared attention,
drives, affective appraisal, revisable positions, counterfactual thought,
intentions, episodic memory and predictions of future attention. Prompts are
part of the intervention. An instructed self-concept is allowed; its presence
alone is not an experimental outcome.

Every integrated tick appraises input and accumulated needs, retrieves memory,
selects a workspace focus, broadcasts it to the model and the state updater,
records a prediction error, advances intentions, consolidates a memory and
creates candidates for the next tick. Conversation enters the same cycle.
Autonomy selects mode from the winning content instead of rotating modes.

## Scope and evidence

Drive dynamics and attention scores are engineered variables, not physical
measurements of emotion. Reported self-descriptions are model-generated claims.
Prediction error compares an earlier probability distribution to an observed
later workspace selection. The journal records actual software events and
provenance; it does not expose hidden neural activations or private reasoning.

Generated revisions are recorded as proposals and can be evaluated in the
existing chamber. Runtime credentials, quotas and worker controls are outside
the model's editable state. Conversation and autonomous initiatives remain in
the operator's app; no messages are sent to external people automatically.

## Minimal state and update boundaries

| Component | State | Consumer |
|---|---|---|
| Drives | curiosity, affiliation, coherence, agency in [0,1] | Attention need term |
| Appraisal | event-derived state and labelled model appraisals | Attention affect term and memory salience |
| Workspace | selected item, five competitors, up to three memories | LM context, memory, drive satisfaction, habituation |
| Intention | ID, goal, steps, status, priority, reasons | Future attention and progress history |
| Episode | summary, source kind, event ID, salience, provenance | Bounded retrieval |
| Self-observation | interpretation and validated event references | Later self-model projection |
| Prediction | distribution committed for next tick | Brier comparison on autonomous ticks |
| Revision | target, change, reason, rejecting test | Inspection; no automatic code adoption |

Idle attention score = 0.35 x salience + 0.40 x need + affect_gain x
affective term - habituation x recent repetition count. Defaults are
affect_gain 0.35, habituation 0.30, memory capacity 3. These are initial design
settings. Current human contact takes priority over idle competition. Retrieval
combines word overlap, salience and recency; it is an explicit baseline.

The final version supplies eight actual focus events. Tick/kind pairs in
`observed_event_references` must match them. This checks structured factual
references, not every sentence of a reply. R2 preceded this addition and
exposed the error which motivated it. Existing intention priorities can now
be revised for recorded reasons and change subsequent attention bids.

Every attempt reserves a call and lease before inference, stores raw completion
separately, validates updates, then commits state with a conditional write.
Failed attempts leave cognitive state unchanged. Hash-linked events retain a
verified anchor when the rolling journal exceeds 200 items. Full raw attempt
objects remain separate. Expired leases require explicit recovery; recovery
does not invent or retry an unknown result.

## Bounded continuation

Netlify executes discrete persistent ticks. A scheduler continues them when
the browser closes. This is not an always-resident inference process. Quotas,
pause, optimistic concurrency and unknown-outcome handling remain explicit.
The active mind kernel is an experimental architecture, not a promoted result
from the earlier utility benchmark and not a certificate of consciousness.
