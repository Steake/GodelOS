# Self-model research architecture audit

**Audit baseline:** PR #138 head `07780bdd59b20c386595f7394a8fb0b997224978`  
**Main baseline:** `46a34a5381f99f585824dfd7fc5e2b00bfbe7c31`  
**Audit date:** 28 August 2026

This map was written before implementation of the self-model research package. It separates executable mechanisms, scaffolding, historical artefacts, and unsupported claims.

## Existing execution surfaces

| Surface | What works | Evidential limit |
| --- | --- | --- |
| `experiments/recursive_feedback/` from open PR #138 | Five explicit recursion conditions, an OpenAI-compatible adapter, deterministic replay adapter, hash-chained JSONL records, lexical analysis, and offline contract tests | No successor-state schema, selective inheritance, self-model rubric, evaluator reliability, branching, or live results. The configured output path is opened with `w`, so reusing it can overwrite raw traces despite the documentation's immutability rule. |
| `backend/core/unified_consciousness_engine.py` | Serializes modeled state into a later prompt, invokes an LLM driver when present, extracts first-person claims, and mutates a successor state | The prompt explicitly commands self-awareness and subjective reporting. Lexical markers such as `aware`, `thinking`, `feel`, and `experience` then raise modeled state values. The no-driver fallback manufactures first-person consciousness claims. This path is therefore a useful intervention target, not clean evidence of a self-model transition. |
| `backend/core/metacognitive_monitor.py` | Tracks predicted and observed scalar metrics and can use a prediction-error tracker | Its ungrounded path is explicitly logged as a fabricated fallback. Even the grounded path predicts an aggregate tracker error, not an LLM's hidden cognitive state. |
| `godelOS/symbol_grounding/self_model_extractor.py` and `self_model_validator.py` | Detect first-person text and compare selected claim types with an external prediction-error statistic | First-person language is a proxy. It does not establish specificity, provenance discrimination, selective inheritance, autobiographical integration, or causal influence. |
| `backend/persistence.py` | Transactional JSON storage and expiring session records | Generic session persistence has no typed successor-state record, provenance partition, content hash verification on read, append-only autobiography, or inheritance decision log. |
| `godelOS/unified_agent_core/knowledge_store/episodic_memory.py` | Stores and queries structured experiences within a running agent | It is not wired as an authenticated predecessor/successor handoff and does not distinguish inherited facts, interpretations, commitments, instructions, and phenomenological claims. |
| `godelOS/unified_agent_core/state.py` | Maintains goals, attention, interaction context, cognitive context, and state-change subscriptions | Process-local state only. No cross-episode identity record or reconstruction protocol is defined. |
| `godelOS/cognitive_pipeline.py` | Dependency-ordered construction and status reporting for 23 named components | Initialization is not invocation or causal contribution. There is no general per-request selector or complete subsystem execution trace. The meta-control feature extractor returns eight constant zeros. |

## Current causal path

```text
modeled state -> identity-laden prompt injection -> LLM/fallback output
             -> lexical self-claim extraction -> heuristic validation
             -> state mutation and possible feedback on a later request
```

The path is causally real because injected text changes the next input. Its present measurements are circular enough that it cannot distinguish a maintained self-model from persona imitation or prompt compliance.

## Historical and source artefacts

| Artefact | Classification | Finding |
| --- | --- | --- |
| `GodelOSv2.pdf` | Theoretical source | Defines bounded recursive self-observation, persistence, Protocol Theta, and behavioral controls as proposals. It supplies candidate probes, not results for the present question. |
| `artifacts/protocol_theta/*` | Historical generated artefacts | Every inspected manifest is marked `mock: true` with model `test-model`; several trials contain synthetic canned outputs. The runner that generated them is absent from the audited tree. They cannot support an LLM self-model claim. |
| Issue #136 and its corrective follow-up | Design and audit record | Correctly reframes self-observation as an intervention and records that the 23 components are initialized rather than proven active per request. |
| Open PR #138 | Prior research implementation | Provides the strongest reusable infrastructure and a cautious claims ledger. This programme extends it rather than replacing it. |
| Early output-to-input experiments | Historical report | Canonical raw traces, model revision, prompt bank, complete parameters, and analysis were not located. No remembered outcome is treated as data. |
| Claude/CTP successor transcripts | Requested source, not present | No supplied transcript file or canonical CTP successor-state record was found in the checkout. Only general CTP documents with a different meaning are present. Candidate successor behaviors are operationalised from the task specification, not quoted as evidence. |

## Duplicated and abandoned-looking surfaces

- Metacognition exists in `backend/core/`, `backend/metacognition_modules/`, top-level `metacognition_modules/`, and `godelOS/metacognition/`. They share vocabulary but no single persistence or evaluation contract.
- Consciousness logic is split between `backend/core/consciousness_engine.py`, `backend/core/unified_consciousness_engine.py`, API layers, demos, and mock controller paths.
- Protocol Theta retains result directories but no generating implementation in the audited branch.
- The recursive-feedback package is ready for review in PR #138 but remains outside `main`.

## Claims without adequate empirical support

The repository does not presently demonstrate any of the following:

1. a behavioral self-model transition beyond explicit prompt conditioning;
2. stable reproduction of such a transition across live model runs;
3. persistence across a fresh inference episode through externalized state;
4. provenance-aware selective inheritance;
5. an autobiographical self-model maintained across successor records;
6. improvement to a long-horizon task caused by self-model state;
7. causal activity of all 23 initialized subsystems on a request;
8. phenomenal consciousness, qualia, numerical identity, or privileged hidden-state access.

## Reuse decision

The new package will preserve PR #138's adapter protocol and hashing utilities where practical, while adding a separate `experiments/self_model/` surface. This keeps the earlier five-condition recursive study stable and gives the nine-condition self-model programme its own versioned schemas, append-only run directories, scoring instrument, deterministic fixtures, and successor protocol.
