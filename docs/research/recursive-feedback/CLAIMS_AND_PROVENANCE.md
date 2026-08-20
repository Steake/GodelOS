# Claims and provenance ledger

**Scope:** recursive output-to-input experiments, observer-state injection, and
their relationship to the GödelOS runtime  
**Repository baseline audited:**
[`46a34a5381f99f585824dfd7fc5e2b00bfbe7c31`](https://github.com/Steake/GodelOS/commit/46a34a5381f99f585824dfd7fc5e2b00bfbe7c31)  
**Audit date:** 20 August 2026

This ledger prevents architectural intent, implemented behavior, remembered
experiments, and empirical results from being collapsed into one story. A claim
may be interesting and still lack evidence. That is a reason to test it, not a
licence to write the result in advance.

| ID | Claim | Status | Evidence or test required |
| --- | --- | --- | --- |
| C01 | An early GödelOS experiment used a model's output as its next input and produced trajectories worth systematic study. | **Historical report; raw evidence not located.** | Issue [#136](https://github.com/Steake/GodelOS/issues/136) publicly discusses the loop, but the repository audit did not locate a canonical prompt set, raw trace, model revision, parameters, timestamps, or analysis for the early run. Reconstruct; do not report remembered outcomes as results. |
| C02 | The present unified runtime can serialize cognitive-state fields into the next LLM prompt. | **Implemented.** | [`backend/core/unified_consciousness_engine.py`](https://github.com/Steake/GodelOS/blob/46a34a5381f99f585824dfd7fc5e2b00bfbe7c31/backend/core/unified_consciousness_engine.py) defines `CognitiveStateInjector.inject_cognitive_state` and calls it from `process_with_unified_awareness`. |
| C03 | A response can update successor state in that runtime path. | **Implemented.** | The same file calls the LLM driver, processes the response through the self-model loop, and updates unified state. This supports a state-transition description. It does not establish that the state is a faithful readout of hidden model cognition. |
| C04 | “Observation” in the prompt is passive and leaves the observed process unchanged. | **False by construction.** | Appending a state representation changes the next model input. The correct causal description is an observer-state **intervention**. The protocol therefore compares accurate and sham state blocks against no-state controls. |
| C05 | The cognitive-pipeline class constructs 23 named subsystem objects. | **Implemented at initialization.** | [`godelOS/cognitive_pipeline.py`](https://github.com/Steake/GodelOS/blob/46a34a5381f99f585824dfd7fc5e2b00bfbe7c31/godelOS/cognitive_pipeline.py) contains 23 subsystem attributes and factory calls. [`docs/SUBSYSTEM_ACTIVATION_STATUS.md`](https://github.com/Steake/GodelOS/blob/46a34a5381f99f585824dfd7fc5e2b00bfbe7c31/docs/SUBSYSTEM_ACTIVATION_STATUS.md) reports successful initialization. |
| C06 | Successful initialization means every subsystem performs meaningful work on every request. | **Not established.** | Initialization, availability, invocation, and causal contribution are different propositions. Per-request call traces or counters are required. Some components are routed, some are side channels, and some contain placeholder behavior. |
| C07 | A general task selector currently chooses an optimal subset from all 23 subsystems. | **Not found in the audited code.** | `InferenceCoordinator` routes among particular proving strategies, but that is not evidence of a general 23-way task router. The earlier issue answer describes this as intended architecture and should not be read as current implementation. |
| C08 | The global workspace's seven registered state categories are the same thing as the 23 cognitive-pipeline subsystems. | **Incorrect.** | `backend/core/unified_consciousness_engine.py` registers seven broad consciousness-state sources. `godelOS/cognitive_pipeline.py` constructs a separate set of 23 reasoning, language, grounding, learning, and control components. The two counts refer to different taxonomies. |
| C09 | Snapshot immutability, bounded recursion, uncertainty tracking, salience filtering, and claim-level provenance are all enforced end to end in the recursive LLM path. | **Partly intended; end-to-end guarantee not established.** | The repository contains related state, monitoring, and salience machinery, but this audit did not find one enforcement boundary proving all five controls for every recursive transition. Treat them as requirements and test them separately. |
| C10 | Recursive trajectories demonstrate consciousness, phenomenal identity, or privileged introspective access. | **Not established and outside the confirmatory claims.** | Textual self-reference and stance continuity admit ordinary prompt-conditioning explanations. Relevant work finds model-, task-, and intervention-dependent self-report behavior. Hidden-state or causal tests are needed even for narrower functional-introspection claims. |
| C11 | Recursive inference is an instance of model collapse. | **Category error unless qualified.** | Shumailov et al. study models retrained across generations on generated data. This project studies repeated inference with fixed weights. The mechanisms may share informal feedback language, but the experimental objects differ. |
| C12 | A 2026 study independently used stateless output-to-input loops for black-box backdoor detection. | **Published adjacent evidence.** | Hasan and Hossain, [arXiv:2608.11348](https://arxiv.org/abs/2608.11348), compare exact self-feeding with repeated same-prompt calls. That later application concerns backdoor detection and does not supply missing evidence for early GödelOS runs. |

## Evidence classes used in this package

- **Implemented:** directly inspectable in the pinned repository snapshot.
- **Documented:** asserted by repository documentation but not independently
  demonstrated by the present audit.
- **Historical report:** described in an issue, note, or recollection without a
  recoverable primary trace.
- **Hypothesis:** a falsifiable proposition registered before data collection.
- **Result:** reserved for an analysis derived from archived raw traces under a
  frozen protocol. This package contains no confirmatory result yet.

## Publication gate

A results revision may replace “registered/reconstruction manuscript” only when
all of the following exist:

1. a committed protocol and prompt-bank hash predating confirmatory collection;
2. immutable model identifiers or an explicit alias-instability limitation;
3. raw JSONL traces plus manifests and hashes;
4. a frozen analysis commit;
5. blinded human annotations with an adjudication log where applicable;
6. null, heterogeneous, and adverse outcomes reported alongside positive ones;
7. an updated ledger linking every empirical sentence to an archived artefact.
