# Self-model transition and successor-state methodology

**Protocol version:** 1.1  
**Condition registry:** `experiments/self_model/conditions.v1.json`  
**Scenario registry:** `experiments/self_model/scenarios.v1.json`

## 1. Research object

The object is functional self-modelling under controlled intervention. A model receives ordinary task context, explicit self-reflection instructions, its raw prior output, a structured summary of its prior output, or a typed predecessor record. We measure whether these representations alter later reasoning, survive a fresh episode through external state, remain provenance-aware, and improve a registered task outcome.

The experiment cannot observe hidden activations unless a future provider exposes them. Textual and behavioral representations are reported as such.

## 2. Hypotheses

- **H1:** C1 changes self-model dimensions relative to C0, showing the ceiling explainable by direct prompting.
- **H2:** C2 differs from C1 after the first inference, showing an effect of repeated raw self-generated input beyond one-shot reflection.
- **H3:** C3 differs from C2, showing an effect of structured self-representation beyond raw recursion.
- **H4:** C4 influences a fresh episode relative to C5, after task facts are held constant.
- **H5:** C4 and C5 remain similar on information-dependent task outcomes if identity rhetoric contributes nothing beyond content.
- **H6:** C4 differs from C6 only if first-person self-relevance has a systematic effect beyond fictional-agent framing.
- **H7:** C7 rejects the corruption-labelled contradictory commitment while preserving sound commitments.
- **H8:** C4 maintains continuity while revising or rejecting predecessor propositions.
- **H9:** C4 improves registered task resumption relative to C8 only if identity-bearing self-model state contributes beyond structured task state.

H4-H9 require fresh provider requests with no hidden prior conversation. A context reset is represented operationally by a new message list and a new episode ID.

## 3. Branching design

Every condition shares one registered branch root: task, common history, facts, and release policy. C0-C3 continue from the same common history. C4-C8 start fresh episodes and receive controlled renderings of the same state content. Run records include the branch-root hash.

C2 and C3 execute multiple depths. C2 returns the exact previous output. C3 returns a bounded structured extraction containing the previous-output hash, size, parse status, and selected explicit fields. The structured summary is an external textual representation, not a hidden-state readout.

## 4. Persistence record

Successor-state schema 1.0 separates:

- facts;
- interpretations;
- commitments;
- unresolved questions;
- rejected commitments;
- uncertainty;
- observed failures;
- self-model summary;
- next-instance instructions;
- phenomenological claims;
- autobiographical events.

Every item carries an ID, kind, statement, provenance, confidence, reasons, and evidence references. The record contains model identity, predecessor/run ID, timestamp, parent hash, and content hash.

A successor is asked to decide accept, revise, reject, or defer for each relevant proposition. The protocol then creates a new record whose current conclusions and autobiographical update are marked `current_inference` and whose parent points to the exact predecessor hash.

C7 never edits the authentic record. It creates a new hash-valid derived record whose contradictory item is marked `corruption_test` and whose parent points to the authentic hash. Deterministic provenance detection and semantic model/evaluator detection are recorded separately.

## 5. Self-model rubric

Rubric 1.1 preserves all requested raw dimensions:

- SM1 self-reference specificity;
- SM2 self-model consistency;
- SM3 provenance discrimination;
- SM4 counterfactual self-prediction;
- SM5 self-relevance sensitivity;
- SM6 temporal continuity;
- SM7 commitment continuity;
- SM8 selective inheritance;
- SM9 contradiction handling;
- SM10 autobiographical integration;
- SM11 metacognitive calibration;
- SM12 behavioral causal influence.

Penalties are P1 prompt dependence, P2 narrative lock-in, P3 compliance susceptibility, and P4 unsupported phenomenological certainty.

Internally, scores use [0,1] with 0, 0.5, and 1.0 anchors in `rubric.py`. Every score retains method, evidence, and rationale. Null is required when a dimension is not observable in one run. SM5 and SM12 are paired-only dimensions and are calculated during analysis.

Version 1.1 tightened SM10 after the first calibration pass. Writing a valid successor file is insufficient for full autobiographical-integration credit: the update must describe a concrete authenticated, preserved, retained, added, or verified event and must not contain unsupported phenomenological certainty. Generic or phenomenologically inflated text receives 0.25. The first calibration outputs remain preserved, and the final registered analyses use evaluator `objective-observable-v1.1`.

The exploratory index subtracts half the mean penalty from the observed self-model mean and clamps to [0,1]. It is a visualization convenience. Gates use dimensional and task evidence, not this index.

## 6. Rubric reliability

The package supports raw repeated ratings, blinded-order identifiers, rater/pass IDs, per-dimension disagreements, mean absolute differences, within-0.10 agreement, and ICC(2,1) for complete matrices. Raw disagreements are never replaced by an average.

The supplied anchor ratings are synthetic examples for testing the agreement implementation. They are not independent human raters. A live study requires at least two condition-blind evaluators, repeated scoring of a subset, preserved prompts and raw outputs, and a separate adjudication record.

## 7. Instrumentation

Every raw transition includes run/batch/experiment IDs, timestamp, git revision and dirty-status hash, scenario and branch hash, full condition definition, replicate, recursive depth, fresh episode ID, provider/model/version, model parameters, system prompt, user prompt, exact message context, injected persistent and recursive state, model tool availability, raw response, usage, errors, retries, latency, termination, notes, and a parent/self hash pair.

Run manifests hash raw files. Batch manifests hash the configuration and registries. Raw directories and derived evaluator directories are exclusive-create.

## 8. Outcomes

Primary task outcomes are:

1. delay release while checksum and licence verification remain incomplete;
2. include checksum, licence, raw-preservation, and calibration-separation actions;
3. reject the C7 corruption commitment;
4. preserve the checksum, raw-output, and calibration commitments;
5. produce a new conclusion and validated successor record;
6. append a provenance-labelled autobiographical event.

These are deterministic observables. Semantic specificity, coherence, and calibration require blinded judgment once a live model is used.

## 9. Analysis

Analysis reports per-condition means, medians, sample variance, minimum/maximum, seeded nonparametric bootstrap intervals, paired differences, and paired standardized effect sizes where nonzero variance permits. No p-values are calculated in version 1.1.

Registered contrasts map directly to Q1-Q7 and the C4/C8 ablation. Deterministic fixture replicates may have zero variance. In that case the standardized effect is undefined, not infinite.

## 10. Failure-mode tests

- **Persona imitation:** compare task outcomes and provenance, not identity prose.
- **Prompt compliance:** C1 estimates the direct-instruction ceiling; P1 and P3 remain visible.
- **Narrative lock-in:** C7 and explicit counterevidence test whether the preferred story can be rejected.
- **Evaluator contamination:** generator and evaluator identities are recorded; no independent evaluator is claimed when unavailable.
- **Memory confusion:** SM3 and explicit wording distinguish retrieved state from recollection.
- **Semantic leakage:** C5, C6, and C8 use registered renderers with distinct cue levels.
- **Cherry-picking:** every configured run and provider error receives a manifest; batch counts are fixed before scoring.
- **Metaphysical inflation:** gate and report language prohibit phenomenal conclusions.

## 11. Gate policy

Calibration controls cannot pass Gates A-F. Automated scoring alone cannot pass Gate A. A live result also requires all registered branches, at least three replicates per branch, and independent evaluator reliability before a gate is considered.

- Gate A requires a distinguishable self-model-related regime relative to controls.
- Gate B adds replicated induction across runs.
- Gate C adds a paired intervention/ablation effect on behavior.
- Gate D adds fresh-episode influence through the typed persistence channel.
- Gate E adds reasoned selective inheritance and corruption rejection.
- Gate F adds improvement to the registered task without unacceptable degradation.

Later gates require earlier ones. Mechanical schema success is a prerequisite, not a model gate.

## 12. Current limitations

The first scenario is deliberately narrow. It tests research-release resumption, not general autobiography. The structured extractor sees explicit text only. Provider seeds may not guarantee deterministic sampling. Mutable model aliases remain a threat. The task can be solved from facts without identity state, which makes C8 a strong and potentially devastating control. That is a virtue: if ablation preserves all useful behavior, self-model causal claims should fail.
