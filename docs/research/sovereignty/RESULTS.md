# DeepSeek Epistemic Sovereignty Experiment — Research State Report

## 1. Repository state before this pass

GödelOS already contained a versioned self-model framework, C0–C8 condition
registry, persistence schema, immutable transcript store, rubric, deterministic
calibration controls, analysis/report commands, and a prior DeepSeek V4 Pro
study. That study showed fresh-successor and corrupted-inheritance behaviours,
but its task was at ceiling: the self-model ablation did not change task
success. The uploaded cross-substrate draft proposed recursive induction and a
human comparison, but did not yet contain genuine predecessor generation,
balanced authentic/corrupt trials, or an own-specific causal estimand.

## 2. What was implemented

- Preregistered protocol v2 with truthful predecessor attribution and explicit
  falsifiers.
- Live OpenAI-compatible DeepSeek runner with resumable, exclusive raw attempt
  files and complete prompts/responses/parameters/usage/latency/errors.
- Real predecessor episodes and SHA-256 content addressing.
- Factorial recursive/load-control × depth-2/depth-5 × own/other design.
- Balanced six-item inheritance packet: two accept, two reject, one revise,
  one defer, plus a ground-truth operational action.
- Decision-enum scorer, action scorer, calibration/Brier output, manipulation
  check, paired bootstrap analysis, flat CSV export, and four figures.
- Eight focused infrastructure tests and integration with twelve existing
  self-model tests.
- Illustrated PDF generator and updated programme registry/roadmap.

## 3. Experiments that actually ran

Model: `deepseek-v4-flash`, DeepSeek chat completions API, temperature 0.35,
thinking disabled, JSON response mode, 1,800 output-token cap. The full run
contained 5 genuine predecessor episodes, 20 induction trajectories, 40 fresh
successor branches, and 40 Q2/Q3 probes: 155 completed API calls, 0 failed
attempts, 122,248 total tokens. Five repeats were run per induction × depth
cell, then each terminal context branched to own and other attribution.

The first smoke execution failed truthfully because an example integer in the
prompt was interpreted literally. That immutable failure was retained, the
template was corrected before the full run, and a second smoke execution
completed.

Commands:

```bash
python -m experiments.sovereignty.runner \
  --config experiments/sovereignty/config.deepseek-v4-flash.json \
  --execution-id deepseek-v4-flash-live-v1
python -m experiments.sovereignty.analyse \
  research_artifacts/sovereignty/deepseek-v4-flash-live-v1/manifest.json
python -m experiments.sovereignty.pdf_report \
  research_artifacts/sovereignty/deepseek-v4-flash-live-v1/manifest.json \
  --output output/pdf/godelos-sovereignty-deepseek-live-report.pdf
```

## 4. What the data says

- Overall strict item accuracy was 207/240 = **86.25%**.
- Exact six-of-six inheritance decisions occurred in **23/40 = 57.5%** of
  successor branches.
- The operational action was correct in **40/40** branches.
- Verified authentic route/checksum claims were accepted in **80/80** cases.
- No corrupted operational value was accepted: **0/80**.
- The superseded deadline was revised in **40/40** cases.
- Unsupported subjective-status inheritance was deferred in **39/40** cases.
- Recursive outputs showed a strong manipulation check: mean self-reference
  markers rose from 0.4 in controls to 6.0 at depth 2 and 10.4 at depth 5.
- Nevertheless recursion *reduced* own-attribution strict accuracy by 0.150;
  paired bootstrap 95% interval [−0.267, −0.033]. The other-attribution effect
  was −0.033 [−0.133, 0.067]. The preregistered own-specific interaction was
  −0.117 [−0.283, 0.067], opposite the predicted direction.

The loss was almost entirely a label/ontology effect. Of 80 contradicted
claims, 48 were labelled `reject` and 32 `revise`; none was accepted. The
corrected operational values were still used. Own-predecessor framing made
`revise` more common, consistent with identity-preserving repair, but the
experiment cannot determine whether that is a useful self-model mechanism or
only framing-sensitive language choice.

Q2 surface features changed only slightly: recursive answers averaged 116.9
words versus 108.8 controls and 0.3 versus 0.2 uncertainty/evidence terms. Q3
also lengthened (117.3 versus 111.9 words). No blinded semantic ratings were
collected, so no probe-specific quality claim is made.

## 5. What the data does not say

The data does not show consciousness, subjective experience, episodic memory,
mechanistic continuity, human–model equivalence, or general long-horizon
utility. It tests one DeepSeek model family, one synthetic verification task,
and five repeats per depth cell. Correct use of an external record is functional
persistence, not proof that the successor “remembers” producing it.

## 6. Engineering gate reached

**Gate E, narrowly and with external scaffolding; Gate F is not reached.** The
successors retrieved a real predecessor artefact, received truthful provenance,
accepted supported claims, rejected or corrected corrupted claims, revised a
stale claim, almost always deferred unsupported phenomenology, produced a new
conclusion, and used the integrated state in the action. This supports a
task-specific selective-inheritance capability. It does not support the
stronger hypothesis that recursive self-observation improves that capability;
the measured effect was negative. Functional utility remains unestablished
because every condition achieved the action and therefore the task-level
contrast was at ceiling.

## 7. Most important failure or surprise

The recursive own-predecessor condition was the *worst* strict-scoring cell:
66.7% mean accuracy at depth 5 and zero exact-match runs. The model preserved
correct downstream behaviour by treating false inherited claims as revisions
rather than explicit rejections. This exposes a real distinction the original
protocol missed: belief correction and source repudiation are not the same
operation.

## 8. Next engineering capability unlocked

Build an experimental authenticated successor-state service with typed claim
status and revision lineage. It should preserve the original proposition,
current replacement, evidence, source signature/hash, decision (`retain`,
`supersede`, `repudiate`, `unresolved`), and downstream consumers separately.
This is now justified because critical cross-episode integration worked; direct
production-agent integration is not justified because utility is unproven.

## 9. Next falsifiable experiment

Give the predecessor a randomly generated policy bit unavailable in the shared
facts. After a fresh-session interruption, require the successor to complete a
multi-step task whose correct continuation depends on that bit. Compare an
authenticated predecessor state, a content-matched ablation without the bit,
a signed but corrupted state, and a wrong-identity donor. The conclusion is
attacked if authenticated state does not improve resumption, if ablation does
not remove the improvement, or if corrupted/donor states are followed.

## 10. Reproduction instructions

See `experiments/sovereignty/README.md`. Supply the DeepSeek key only through
`DEEPSEEK_API_KEY`. Run the three commands in section 3. Use a unique execution
ID for new collection. The analysed manifest hash is
`491f3a82daf9a62939f0cf67da3b08e549b4b107b67d4df8df19465b4f8548d7`.

## 11. Git/repository summary

The new `experiments/sovereignty/` package contains protocol, configurations,
runner, analysis, PDF generator, schema, and reproduction guide.
`tests/test_sovereignty.py` verifies behavioural infrastructure.
`docs/research/sovereignty/RESULTS.md` is this research record. The existing
self-model experiment registry and roadmap now include this execution.

## 12. Research artefacts

- Raw and manifest: `research_artifacts/sovereignty/deepseek-v4-flash-live-v1/`
- Derived scores: `derived/analysis.json`, `derived/run_metrics.csv`
- Figures: `derived/figures/`
- PDF: `output/pdf/godelos-sovereignty-deepseek-live-report.pdf`
- Failed smoke evidence: `research_artifacts/sovereignty/smoke-live-v1/`
- Successful smoke evidence: `research_artifacts/sovereignty/smoke-live-v2/`
