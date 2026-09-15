# GödelOS V10 workspace

## V10.1 live cognition

Conversation and operator-started thought cycles now use an NDJSON streaming
endpoint. The interface renders the reply as provider tokens arrive and names
the durable execution phases: input reservation, context assembly, model
response, output validation and state commit. Streamed prose is provisional
display data. No autobiographical, belief, intention or self-model update
becomes authoritative until the complete structured response passes validation
and the atomic state write succeeds. Other mutation requests use the same
global operation indicator so the operator sees elapsed time, success or
failure instead of an inert button.

## Audit and scope

The existing Netlify package already had an attention competition, engineered
appraisal, memories, intentions, self-observation, bounded personality changes,
an autonomous scheduler, a controlled experiment workbench, and a signed
attention-policy evolution chamber. V10 connects and repairs those components;
it does not replace the repository's independent Python/Svelte architecture.

`lib/core.mjs` owns beliefs and the event chain. `mind.mjs` selects attention and
constructs model context. `mind-runtime.mjs` serialises chat and autonomous calls,
retaining immutable raw attempts. The scheduled worker continues without a
browser. The evolution chamber remains a restricted expression compiler, not
arbitrary code execution or model-weight editing. The canonical UI is under
`godelOS/cognitive_sovereignty/web_assets`; the builder copies it into `public`.

## Implemented

- V8-to-V10 mind migration preserves existing state and identity.
- Stance revisions retain before/after values, reasons, provenance and episode.
- Six state interventions execute before selection and prompt construction.
- Current workspace citations are validated against the actual current event,
  alongside historical events. Invented event references remain rejected.
- Background contention defers without spending an unused provider reservation.
- The operator can inspect background status/budget and recover a blocked worker.
- The live input graphic shows real recorded attention bids and their components,
  retrieved/cited memory, stance changes and intention updates.
- Shared light/dark colours cover legacy Value Lab, Calibration, forms and saved
  investigations. Layouts use shrinkable columns rather than hiding overflow.
- Pending/failed messages remain visible; drafts survive refresh and theme changes.
- Observed premature root/object closures are repaired only at supported,
  unambiguous boundaries. Values are preserved; raw text and repair hashes remain
  available. Duplicate fields, ambiguous repairs and truncation are rejected.
- A uniquely nested diagnostic is normalised with a receipt. Six exact provider
  failures have regression fixtures; fresh live verification follows the fixes.
- Redundant trailing closures and literal control characters in JSON strings
  have value-preserving repairs. Genuine truncation still cannot invent missing
  state: the complete reply is delivered when available and the update is held.
- Diagnostic output places required fields first, omits empty boilerplate and
  uses a 4,000-token default ceiling. All arms use the same configured budget.

## Final verification

86 Node tests pass. Six exact provider-format fixtures pass offline repair tests.
All 18 real responses from the compact diagnostic pass the final parser offline;
two fresh targeted DeepSeek requests pass without any repair. The original
failed rows remain in each collection, distinct from the final parser replay.
The retained pass contains 110 real provider responses in total: a 54-call
diagnostic, three 18-call engineering checks and two final targeted calls.
See `research/workspace-v10/RESULTS.md` in the deployment package for the counts,
limitations and exact reproduction commands. No production deployment occurred.

## Diagnostic

Full state, self-model removed, affect disconnected, autobiography removed,
content-matched reference state, and no inherited state. Three phases per arm:
contradiction, unrelated interruption, delayed cross-domain transfer. All model
parameters and the response schema are held constant. Authorship and task
answers are deterministic fixture code; the model never receives the oracle.

This is an instrument diagnostic with deliberately easy factual controls, not
a powered test of identity superiority. Citations are observable reports and
are not automatically proof of causal use. No result automatically promotes an
identity-bearing controller. No phenomenal measurement or weight change is
claimed. Full vs content-matched is the identity-framing comparison; the other
ablations deliberately remove different information pathways.

The execution environment reset during an earlier attempt in this conversation.
Those lost raw files are excluded from the retained analysis. Only runs actually
present in this package contribute to the report's counts and charts.

## Operator route

Conversation is the front door. Click its input graphic to open Activity. Run
one thought or a short exploration, open Positions & changes of mind, then use
Experiments to design and run controlled research. Background thinking follows
the Netlify schedule, while multi-round workbench/evolution campaigns still
advance from the browser. Closing the page does not continue those campaigns.

## V10.1.1 autonomous failure recovery
Confirmed failed episodes schedule fresh attempts with 15/30/60 minute capped backoff. Daily quotas and operator pause remain authoritative. Legacy blocked failures and expired unknown outcomes are reconciled on scheduler ticks before a later fresh dispatch. Original reservations and immutable evidence remain intact; original calls are never replayed. Scheduler cadence can add up to 15 minutes to eligibility. Provider content received before transport failure is retained, complete prose is delivered with cognitive updates quarantined, and incomplete prose is never represented as a completed reply. Browser disconnect recovery uses bounded read-only evidence lookups.

Validation: 92 Node tests pass, including failure-to-fresh-dispatch, legacy reconciliation and interrupted-stream recovery. The user-supplied production reference was not retrieved; validation uses deterministic injected faults.
