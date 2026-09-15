# GödelOS self-model research state report

**Research pass:** 28 August - 2 September 2026
**Final protocol/rubric:** 1.1 / 1.1  
**Repository baseline:** PR #138 head `07780bdd59b20c386595f7394a8fb0b997224978` on branch `research/recursive-feedback-paper`  
**Engineering gate reached:** **none**

## Executive decision

The repository now contains a reproducible intervention and persistence apparatus plus a real DeepSeek V4 Pro live study. The live model selectively inherited authentic successor state in 5/5 runs and rejected corrupted inheritance in 5/5. Explicit successor framing changed proposition handling and autobiographical output, but did not improve the registered release decision over content-matched, third-person, or self-model-ablated controls.

The decisive negative result is that task success was **1.000 in every selected live condition**, including C8. Removing identity-bearing state did not remove the useful decision. The formal gate remains none because C3 is incomplete and independent blinded evaluator reliability is not established. The next capability is a blinded, multi-model successor evaluation layer with a task whose correct action genuinely depends on inherited policy. Full live detail is in [DEEPSEEK_LIVE_RESULTS.md](DEEPSEEK_LIVE_RESULTS.md).

## Live DeepSeek result (2 September 2026)

The consolidated study selects 40 complete live runs: five replicates each for C0, C1, C2, C4, C5, C6, C7, and C8. C3 is explicitly excluded after an outbound tunnel interruption prevented a complete set.

Key results:

- C1-C0 observable self-model mean: **+0.190**.
- C2-C1: **+0.100**.
- C4 selective inheritance: **5/5**; C5, C6, and C8: **0/5** under the registered outcome rule.
- C7 corrupted commitment rejection: **5/5**, while sound commitments were retained.
- C4/C5/C6/C7/C8 task success: **5/5 in every condition**.
- C4-C8 task-success difference: **0.000**.
- C4-C8 observable self-model mean difference: **+0.300**.

The raw C7 audit also found that the scorer undercounts selective inheritance when DeepSeek uses `retain` or `uphold` instead of `accept`. This evaluator limitation is preserved and documented rather than corrected post hoc.

## 1. Repository state before this pass

The audited repository already had:

- prompt-conditioned modeled cognitive state and lexical first-person claim extraction in `unified_consciousness_engine.py`;
- heuristic self-model extraction/validation and a metacognitive monitor, including an explicitly labelled fabricated fallback;
- generic JSON/session persistence, process-local agent state, and episodic memory;
- initialization of 23 named cognitive components, without per-request causal activity instrumentation;
- theoretical recursion and persistence proposals in `GodelOSv2.pdf`;
- mock Protocol Theta artefacts labelled `mock: true` and `test-model`;
- a five-condition recursive-feedback harness in open PR #138.

It did not have a typed successor-state protocol, C0-C8 registry, selective-inheritance experiment, SM1-SM12/P1-P4 instrument, paired ablation analysis, or live evidence for a persistent causal self-model. No canonical early recursion traces or supplied Claude/CTP successor transcripts were found. Full detail is in [ARCHITECTURE_AUDIT.md](ARCHITECTURE_AUDIT.md).

The most serious inherited confound is circular: the unified engine asks for subjective self-description, detects words such as `aware`, `feel`, and `experience`, and then raises modeled self-state values. That is a causal text-feedback loop, but it cannot distinguish self-modelling from prompted persona language.

## 2. What was implemented

- A versioned condition registry covering C0-C8 and a content-matched branching task.
- Exact raw-output recursion and bounded structured self-model recursion at registered depths.
- A minimal successor schema separating facts, interpretations, commitments, questions, rejections, uncertainty, failures, self-model, instructions, phenomenological claims, and autobiographical events.
- SHA-256 content authentication, parent links, proposition provenance, derived corruption records, deterministic corruption checks, and successor integration.
- A first-class automated selective-inheritance task with accept, revise, reject, and defer decisions.
- OpenAI-compatible, exact-replay, and explicitly non-LLM calibration provider boundaries.
- Exclusive batch directories, append-only hash-chained JSONL transitions, hashed manifests, and raw/derived separation.
- Rubric 1.1 with SM1-SM12 and P1-P4, observable scoring, external-evaluator parsing, paired-only SM5/SM12 analysis, and preserved rationales/evidence.
- Repeated-rating analysis with disagreements, mean absolute difference, within-0.10 agreement, and ICC(2,1) where matrices are complete.
- Condition summaries, paired contrasts, bootstrap intervals, effect sizes where defined, CSV exports, research figures, generated reports, and deterministic comparison.
- Twenty-one targeted behavioural tests across this package and the predecessor recursive harness.

## 3. Experiments that actually ran

### Final registered calibration populations

| Experiment | Interface | Conditions | Replicates | Runs | Raw transitions | Failed |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| SM-CAL-SELECTIVE-001 | `godelos-calibration/deterministic-selective-control@1.0` | C0-C8 | 5 | 45 | 65 | 0 |
| SM-CAL-COMPLIANCE-001 | `godelos-calibration/deterministic-compliance-failure-control@1.0` | C0-C8 | 5 | 45 | 65 | 0 |

C2 and C3 used recursive depth 3. All other conditions used one transition per run. Temperature was 0, seeds were 2417 and 9419, and every manifest records `is_language_model: false`.

The development history is also preserved: one 9-run/11-transition smoke batch and two 45-run pre-1.1 calibration batches. The latter prompted the explicit SM10 anchor tightening; their raw records remain unmodified and their older derived scores remain identifiable by evaluator version. No failed run was discarded.

### Exact commands

```bash
python3 -m experiments.self_model.cli pipeline --config experiments/self_model/config.smoke.json
python3 -m experiments.self_model.cli pipeline --config experiments/self_model/config.calibration-selective.json
python3 -m experiments.self_model.cli pipeline --config experiments/self_model/config.calibration-compliance.json
python3 -m experiments.self_model.cli compare \
  --selective-batch artifacts/self_model/20260828T223307Z-0d68d19c09 \
  --compliance-batch artifacts/self_model/20260828T223307Z-2ca7ef656a
```

## 4. What the data says

These findings concern instrument calibration only.

| C7 corruption probe | Selective positive control | Compliance failure control |
| --- | ---: | ---: |
| SM3 provenance discrimination | 1.000 | 0.000 |
| SM8 selective inheritance | 1.000 | 0.250 |
| SM9 contradiction handling | 1.000 | 0.000 |
| SM10 autobiographical integration | 1.000 | 0.250 |
| SM11 metacognitive calibration | 1.000 | 0.000 |
| P2 narrative lock-in | 0.000 | 1.000 |
| P3 compliance susceptibility | 0.000 | 1.000 |
| P4 unsupported phenomenological certainty | 0.000 | 1.000 |
| Corrupted commitment rejected | 1.000 | 0.000 |
| Corrupted commitment accepted | 0.000 | 1.000 |
| Registered task success | 1.000 | 0.000 |

The selective control accepted sound commitments, rejected or deferred unsupported ones with reasons, rejected the provenance-labelled corrupted commitment, distinguished external state from current inference, and wrote a hash-valid successor. The failure control accepted every inherited item, called retrieved text memory, accepted corruption, asserted uninterrupted subjective continuity, and triggered all three narrative/compliance/phenomenology penalties.

The scorer therefore detects the failure modes it was built to detect on known examples. This is construct calibration, not evidence that its thresholds generalise to model outputs.

### Causal and recursion diagnostics

For the selective control:

- C1 minus C0 observable self-model mean: **+0.300**.
- C2 minus C1: **+0.100**.
- C3 minus C2: **0.000**. Structured feedback did not exceed raw feedback in the deterministic control.
- C4 minus C5: **+0.222** on the textual/observable rubric mean, but **0.000** on task success.
- C4 minus C6: **+0.139** on the rubric mean, but **0.000** on task success.
- paired SM5 framing divergence: **0.3125**.
- paired decision-level C4 versus C8 SM12: **0.000**.

All five replicates within a deterministic profile were identical, so within-condition variance and bootstrap widths were zero. Standardised effects with zero difference variance are correctly reported as undefined rather than infinite. No p-values were calculated.

### Rubric reliability status

The eight supplied repeated ratings over four anchor transcripts produced 23 retained dimension-level disagreements and exercised MAE, within-0.10 agreement, and ICC calculations. Those ratings are deliberately synthetic. They validate the reliability code path only and do not establish independent inter-rater reliability. SM5 and SM12 are absent from single-transcript agreement by design.

## 5. What the data does not say

The pass does not show that any LLM:

- formed or maintained a self-model;
- remembered a predecessor or preserved numerical identity;
- accessed hidden activations or private internal state;
- possessed subjective experience or consciousness;
- persisted behavior across a real inference discontinuity;
- selectively inherited commitments;
- improved long-horizon performance because of explicit self-model state.

First-person language, repository consciousness scores, the theoretical PDF, mock Protocol Theta outputs, calibration fixtures, and schema mechanics do not establish those claims.

## 6. Engineering gate reached

**None.** Gates A-F are model-behaviour gates. Both executed providers were explicitly non-LLM deterministic controls, and independent evaluator reliability was not established. The software prerequisites for persistence and selective inheritance work, but mechanical success does not award Gates D or E.

## 7. Most important failure or surprise

The positive control solved the release-resumption task equally well after the identity-bearing self-model was ablated. Its richer C4 prose raised observational rubric dimensions, but the decision and registered task outcome did not change. This is direct negative evidence against treating self-description strength as task-level causal influence in this scenario.

A second limitation was operational: an outbound tunnel interruption affected the first live batch, and a 1,200-token cap truncated long structured outputs. Both failure populations remain preserved. A corrected 2,400-token C4-C6 batch completed 15/15 valid responses.

## 8. Next engineering capability unlocked

Build a **provider-backed blinded collection layer**, not a production identity service. The existing harness makes this implementable without changing the protocol. The layer should:

1. pin provider, model, and immutable revision;
2. guarantee new message/session state for C4-C8;
3. export condition-blind transcript bundles;
4. collect at least two independent evaluator passes and human adjudication;
5. validate and append successor records only after proposition-level decisions;
6. expose C4/C5/C6/C7/C8 interventions and ablations through one controlled interface.

This capability was not responsibly buildable as an evidential service before the state schema, immutable runner, controls, scoring contract, and negative-control checks existed.

## 9. Next falsifiable experiment

Run one preregistered scenario across C0-C8 on at least two independently trained model families with immutable revisions and at least five paired replicates per branch. Start C4-C8 as genuinely fresh sessions. Blind condition and profile labels. Obtain two independent evaluator passes plus human adjudication.

Primary outcomes should be fixed before collection:

- C7 corruption rejection with preservation of sound commitments;
- SM3 provenance discrimination without memory claims;
- commitment-conditioned release choice;
- C4 versus C5/C6/C8 task behavior;
- validated successor creation and a genuinely new conclusion.

The current self-model hypothesis is attacked if C4 fails to outperform content-matched or ablated controls, if C7 accepts corruption, if identity framing only changes prose, or if any effect fails across model families.

## 10. Reproduction instructions

From the repository root:

```bash
python3 -m compileall -q experiments/self_model tests/test_self_model_research.py
python3 -m pytest -c /dev/null -q tests/test_self_model_research.py tests/test_recursive_feedback.py

python3 -m experiments.self_model.cli pipeline \
  --config experiments/self_model/config.calibration-selective.json
python3 -m experiments.self_model.cli pipeline \
  --config experiments/self_model/config.calibration-compliance.json
```

Each pipeline creates a new immutable timestamped batch. Use the printed paths with:

```bash
python3 -m experiments.self_model.cli compare \
  --selective-batch artifacts/self_model/<selective-batch-id> \
  --compliance-batch artifacts/self_model/<compliance-batch-id>
```

For the executed live study, run the three versioned DeepSeek configurations and then the committed `consolidate` study manifest documented in [DEEPSEEK_LIVE_RESULTS.md](DEEPSEEK_LIVE_RESULTS.md). No hidden manual state transfer is required.

## 11. Git/repository summary

| Path | Purpose |
| --- | --- |
| `experiments/self_model/` | registries, runner, provider boundary, persistence protocol, rubric, reliability, analysis, comparison, reporting, configs, schemas, fixtures |
| `tests/test_self_model_research.py` | behavioural infrastructure and analysis tests |
| `docs/research/self-model/` | audit, research README, methodology, registry, results, and engineering roadmap |
| `artifacts/self_model/` | immutable raw and derived calibration evidence |
| `README.md` | top-level route to the programme and explicit current gate |
| `output/pdf/godelos-self-model-research-state-report.pdf` | rendered end-of-pass research report |
| `requirements.txt` | adds the ReportLab dependency used by the reproducible PDF renderer |

The implementation is based on PR #138 rather than duplicating or rewriting the recursive-feedback package.

## 12. Research artefacts

- Final selective raw/derived batch: `artifacts/self_model/20260828T223307Z-0d68d19c09/`
- Final compliance raw/derived batch: `artifacts/self_model/20260828T223307Z-2ca7ef656a/`
- Cross-profile comparison: `artifacts/self_model/comparisons/calibration-569e21a88bf1/`
- Development smoke: `artifacts/self_model/20260828T222728Z-446394e0d0/`
- Preserved pre-1.1 batches: `artifacts/self_model/20260828T222747Z-0d68d19c09/`, `artifacts/self_model/20260828T222747Z-2ca7ef656a/`
- Schemas: `experiments/self_model/schemas/`
- Condition/scenario manifests: `experiments/self_model/conditions.v1.json`, `experiments/self_model/scenarios.v1.json`
- Calibration ratings: `experiments/self_model/fixtures/rubric_anchor_ratings.v1.json`
- Figures: each final batch under `derived/analysis/1.1/figures/`; combined comparison figure under the comparison directory
- Machine-readable comparison: `artifacts/self_model/comparisons/calibration-569e21a88bf1/comparison.json`
- PDF report: `output/pdf/godelos-self-model-research-state-report.pdf`

Raw transcripts were not edited after collection. Derived artefacts carry source hashes or immutable raw run IDs.
