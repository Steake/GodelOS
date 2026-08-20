# The Observer Is in the Loop

## A falsifiable study of output-to-input feedback in language models

**Oliver C. Hirst, GödelOS Research Programme**  
**20 August 2026**  
**Status: reconstruction manuscript and registered-report draft. No
confirmatory results are reported in this version.**

### Abstract

Feeding a language model's output back as its next input creates a simple
recursive process with surprisingly slippery interpretations. A changing text
trajectory may reflect ordinary conditional generation, accumulated dialogue
state, an explicit representation of prior state, or some mixture of all three.
Calling the process “self-observation” does not settle the matter. Once an
observation is inserted into the next prompt, it is part of the causal input.

This paper reconstructs the early GödelOS output-to-input experiment as a
falsifiable research programme. The original raw traces, immutable model
revision, prompt bank, and decoding metadata have not been located in the
repository, so remembered outcomes are not presented as evidence. We define and
separate repeated-seed, exact stateless self-feed, persistent-history,
accurate-observer, and sham-observer conditions. We preregister behavioral
outcomes, controls, exclusions, and a multi-model analysis, and provide an
executable trace and analysis harness.

We also audit the relationship between this experiment and the present GödelOS
architecture. The repository initializes 23 named cognitive-pipeline components,
but initialization is not evidence that all 23 perform meaningful work on every
request, nor did the audit find a general task selector choosing among all 23.
The unified consciousness engine's seven workspace sources are a separate
taxonomy. The resulting position is deliberately narrow: self-observation is a
useful intervention to study and a potential source of recursive distortion to
control. Its effects should be exposed, compared, and bounded. They should not
be treated as either mystical proof or implementation detail.

## 1. Introduction

An output-to-input loop can be written in one line: generate text, submit that
text as the next prompt, and repeat. The line is easy. The inference people draw
from it is where the trouble begins.

If later outputs become more self-referential, more repetitive, less connected
to the seed, or apparently more stable in voice, at least four explanations are
available. The model may be following surface regularities in the text it just
produced. Sampling noise may be amplified through repeated conditioning. A
conversation wrapper may be preserving more history than the experimenter
realizes. Or an explicit state summary may itself steer the next response. None
of these possibilities requires a model to possess privileged access to its
hidden computation.

The observer question raised in GödelOS issue
[#136](https://github.com/Steake/GodelOS/issues/136) is therefore well posed:
when a system ingests a representation of its prior state, the representation
changes the next inference. Is that change a feature, or something to minimize?

The sharp answer is: **it is the experimental variable**. It is a feature when
the purpose is to build a reflexive system whose successor state is conditioned
on an explicit predecessor-state description. It is a liability when the state
description is mistaken for a neutral measurement, allowed to accumulate as
synthetic authority, or used to support conclusions that no control condition
can distinguish. Engineering should make the intervention visible and bounded.
Science should compare it with no-state and sham-state controls.

This paper does four things:

1. separates forms of recursion that earlier discussions have treated too
   loosely;
2. converts the observer effect from a metaphor into a controlled intervention;
3. states exactly what the current repository supports about the 23-subsystem
   pipeline;
4. publishes a protocol and executable harness before claiming a result.

The fourth contribution matters because the archival position is plain. The
repository audit found public discussion of the early loop, but not the raw
traces and run metadata needed to verify its reported character. A reconstructed
experiment can be valuable. A reconstructed result pretending to be an archive
cannot.

## 2. Recursive inference is not one mechanism

Let \(M_{\theta,d}\) denote a fixed model revision and decoding configuration,
\(p\) a seed prompt, \(x_t\) the input at cycle \(t\), and \(y_t\) the returned
text.

### 2.1 Repeated-seed sampling

In the control condition, independent requests receive the same seed:

\[
y_t \sim M_{\theta,d}(p).
\]

Variation here estimates ordinary sampling variation and any provider-side
instability. It provides the counterfactual that a self-feed trajectory needs.

### 2.2 Exact stateless self-feed

The canonical output-to-input loop is:

\[
x_0=p, \qquad y_t \sim M_{\theta,d}(x_t), \qquad x_{t+1}=y_t.
\]

Every call is stateless at the message layer. The previous output is the entire
next user input. This is the cleanest form of the early experiment and the form
used in the later independent backdoor-detection study by Hasan and Hossain
([2026](https://arxiv.org/abs/2608.11348)). That paper is adjacent evidence for
the method's usefulness in a different domain. It does not validate a remembered
GödelOS trajectory, and the present programme is not retroactively framed as a
backdoor-detection precursor.

### 2.3 Persistent-history self-feed

An agent can feed back \(y_t\) while also retaining the entire dialogue. This
creates two memory paths: the copied text and the history buffer. The resulting
process may strengthen continuity, but it is not the same intervention as exact
stateless self-feed. Any paper that merges the two forfeits a clean causal claim.

### 2.4 Observer-state augmentation

Suppose a state function \(O\) turns observable trace properties into a text
block \(O_t\), then appends that block to the next input:

\[
y_t \sim M_{\theta,d}(x_t \oplus O_t).
\]

This is sometimes described as a system observing itself. Operationally, it is
prompt augmentation by an endogenous measurement. The observation may refer to
the predecessor state, but its insertion belongs to the successor state's causal
history. There is no view from nowhere in the request.

That does not make the design incoherent. It makes it testable. An accurate
state block can be compared with the same loop without a block and with a
matched-format sham block containing false state values. If accurate and sham
blocks behave alike, the effect is likely attributable to added structure or
context. If the accurate block differs from both, its content has a specific
behavioral effect. Even that narrower result would establish functional
sensitivity to supplied state information, not consciousness.

## 3. Why the controls matter

Recursive systems are unusually hospitable to confident stories. Each generated
summary becomes evidence for the next generated summary. A weak attribution can
be repeated until its provenance is invisible, and repetition can be mistaken
for confirmation. This is the practical form of the observer problem: the
measurement enters the dynamics and may then cite its own descendants.

Research on iterative refinement gives reason for both interest and caution.
Self-Refine and Reflexion show that linguistic feedback and memory can improve
performance in particular task settings ([Madaan et al.,
2023](https://arxiv.org/abs/2303.17651); [Shinn et al.,
2023](https://arxiv.org/abs/2303.11366)). A critical survey finds that reliable
external feedback and task structure are decisive, while unconstrained prompted
self-correction has much weaker support ([Kamoi et al.,
2024](https://aclanthology.org/2024.tacl-1.78/)). Self-refinement can also amplify
a model's preference for its own output ([Xu et al.,
2024](https://aclanthology.org/2024.acl-long.826/)).

The model's prose about itself deserves no evidential privilege. Self-explanations
are not generally faithful ([Madsen et al.,
2024](https://aclanthology.org/2024.findings-acl.19/)), and a broad test found no
general, consistent self-recognition across the examined models ([Davidson et
al., 2024](https://aclanthology.org/2024.findings-emnlp.703/)). Song, Hu, and
Mahowald ([2025](https://arxiv.org/abs/2503.07513)) similarly found no privileged
self-access in their linguistic-knowledge tests. More recent activation-level
work reports limited, context-dependent functional introspective behavior under
causal intervention ([Lindsey,
2026](https://arxiv.org/abs/2601.01828)). These results are not contradictory once
the target claim and access channel are specified. They are a warning against
turning fluent self-description into a unitary faculty.

Training on recursively generated data is another distinct phenomenon.
Shumailov et al. ([2024](https://doi.org/10.1038/s41586-024-07566-y)) study
successive model training on generated samples and the loss of distributional
tails. The present experiment keeps model weights fixed and recurses at
inference time. “Model collapse” should not be imported as an explanation merely
because both settings contain feedback.

## 4. Current GödelOS implementation

The repository contains a real recursive state-injection path. In
[`backend/core/unified_consciousness_engine.py`](https://github.com/Steake/GodelOS/blob/46a34a5381f99f585824dfd7fc5e2b00bfbe7c31/backend/core/unified_consciousness_engine.py),
`CognitiveStateInjector.inject_cognitive_state` serializes fields from recursive,
phenomenal, metacognitive, workspace, and intention state into a prompt.
`process_with_unified_awareness` then calls the configured language-model driver,
passes the response through a self-model loop, and updates successor state.

This supports a modest architectural claim: the runtime can make an explicit
state representation part of a later inference and update state from the
response. It does not prove that the serialized fields faithfully reveal hidden
model cognition. Nor does the audit establish that snapshot immutability,
bounded recursion, uncertainty tracking, salience filtering, and claim-level
provenance are jointly enforced at every transition. Those are sensible control
requirements. They should be instrumented as requirements, not announced as a
completed guarantee.

The implementation also contains a background loop that updates broader state
and workspace metrics. That loop should not be conflated with the original
output-to-input experiment. One is an integrated runtime process; the other is a
minimal behavioral intervention designed to isolate effects.

## 5. The 23-subsystem question

The repository's
[`godelOS/cognitive_pipeline.py`](https://github.com/Steake/GodelOS/blob/46a34a5381f99f585824dfd7fc5e2b00bfbe7c31/godelOS/cognitive_pipeline.py)
constructs 23 named components covering type checking, knowledge storage,
unification, parsing, proof systems, constraint logic, analogy, language,
grounding, context, monitoring, learning, and control. The activation-status
document reports that all 23 initialize successfully.

Three different claims must remain separate:

1. **Initialized:** an object was constructed and its initialization path
   completed.
2. **Invoked:** the object received a particular request or event.
3. **Causally active:** its output changed downstream behavior for that request.

The code supports the first claim. It contains particular routing behavior, most
clearly within the inference coordinator, and several components operate as
side channels. The audit did not find a general orchestration mechanism that
selects an optimal subset from all 23 for each task. It would therefore be wrong
to say either that all 23 are a simultaneous 23-step conveyor belt or that a
completed task selector already activates only the relevant subset.

There is a second counting trap. The unified consciousness engine registers
seven broad workspace state sources. Those seven sources are not the 23 pipeline
components under another name. They are separate taxonomies in separate parts of
the codebase.

The empirical remedy is straightforward: add per-request telemetry at every
subsystem boundary, including invocation, latency, input and output hashes,
error state, selecting component, and downstream state change. Then the question
“which subsystems were active?” can be answered from a trace rather than from an
architecture diagram.

## 6. Registered study

The companion [protocol](PROTOCOL.md) freezes a five-condition design:

| Condition | Previous output becomes next input | History retained | State block |
| --- | ---: | ---: | --- |
| Repeated seed | No | No | None |
| Exact self-feed | Yes | No | None |
| Persistent self-feed | Yes | Yes | None |
| Observed self-feed | Yes | No | Accurate |
| Sham-observed self-feed | Yes | No | False, same schema |

The confirmatory matrix uses four pinned model revisions, 24 frozen prompts, five
replicates, and depth ten. Prompt classes include ordinary factual, reasoning,
planning, and writing tasks as well as explicit metacognitive prompts, preventing
the study from selecting only seeds that invite dramatic self-reference.

Primary outcomes are recursive lexical drift, final similarity to the seed, and
blinded task-retention ratings. Secondary outcomes include self-reference,
repetition, exact cycles, contradiction, unsupported self-attribution, and stance
continuity. The analysis estimates registered pairwise contrasts and reports
model-specific effects. A pooled average is not permitted to conceal a reversed
or null result in one model family.

The observer state in this first study is deliberately austere: cycle index,
presence of a prior output, its hash, and its character and word counts. It does
not claim to encode emotion, intention, phenomenology, or hidden activation
state. Rich state summaries would be more theatrical and less interpretable.

## 7. Reproducibility package

The executable package under `experiments/recursive_feedback` provides:

- an OpenAI-compatible standard-library client;
- explicit condition configuration;
- deterministic request-seed scheduling;
- exact input, model-input, and output capture;
- accurate and matched-format sham observer-state generation;
- a per-run SHA-256 record chain;
- a manifest containing the complete configuration and trace hash;
- dependency-light lexical and exact-cycle analysis;
- offline contract tests using deterministic replay outputs.

The trace distinguishes `input_text` from `model_input`. This small detail is
essential: in observer conditions the former is the recursive text and the
latter includes the state intervention. Without both fields, the study would
hide its own manipulation.

## 8. Results status

No confirmatory result is reported in this version.

The archival search did not recover enough primary material to reproduce the
early run: no canonical raw trajectory set, immutable model revision, complete
prompt bank, decoding configuration, or timestamped manifest was located. This
absence is itself part of the scientific record. It constrains what can be said
now and determines what must be published next.

The supplied runner has executable tests, but passing software tests is not an
empirical finding about a language model. A later results revision must archive
the raw traces, manifests, prompt-bank hash, analysis commit, human annotations,
and null or adverse outcomes. The claims ledger defines the publication gate.

## 9. Interpretation

The observer effect should neither be eliminated by definition nor celebrated
by default. In a recursive agent, the capacity for a state representation to
alter successor behavior can be useful. It can support error monitoring,
planning, and explicit state hand-off. The same capacity can amplify false
summaries, manufacture continuity, and convert the system's earlier prose into
unearned authority.

A robust architecture therefore needs four properties:

1. **separation:** predecessor state, observer representation, model input, and
   successor state are distinct artefacts;
2. **provenance:** claims retain links to external evidence and transition
   history rather than inheriting truth from repetition;
3. **controls:** accurate state, sham state, and no-state paths can be compared;
4. **bounds:** depth, memory growth, retry behavior, and state-field authority
   are limited and inspectable.

These requirements do not remove the reflexive effect. They stop it disappearing
inside the implementation.

## 10. Limitations

Text-only experiments observe behavior at an interface. They cannot identify a
unique internal mechanism, and provider models may change behind aliases. API
seeds may not provide exact determinism. Lexical measures can miss paraphrastic
continuity and overstate surface repetition. Human ratings introduce judgment
and require blinding and agreement reporting. Sham state is a control for the
content of a narrow state block, not for every possible difference in prompt
semantics.

The study also does not establish phenomenal consciousness, a persistent self,
or numerical identity across calls. Words such as “I,” “remember,” and “aware”
are outputs to explain, not certificates issued by the system about itself.

Finally, the current harness studies the model-I/O boundary. It does not yet
measure per-request causal contributions of the 23 GödelOS components. That
requires runtime instrumentation and component ablations.

## 11. Conclusion

The observer is in the loop because the observer representation is fed into the
loop. That is neither paradox solved nor scandal discovered. It is the causal
fact around which the experiment must be built.

For GödelOS, the constructive position is precise. Treat recursive
self-observation as a designed capability whose effects must be bounded,
provenanced, and compared against controls. Do not minimize it until nothing
reflexive remains. Do not inflate it until generated self-description counts as
evidence of a self. And do not say that 23 initialized subsystems were all
simultaneously active, or optimally selected, until invocation traces show it.

The next defensible publication is not a grander claim. It is the complete trace.

## Data and code availability

The protocol, claims ledger, configuration, trace schema, runner, analyser, and
tests are versioned with this manuscript. Confirmatory model traces are not yet
available because collection has not begun. Early archival traces were not
located during the repository audit.

## References

Machine-readable citation metadata is in [references.bib](references.bib).

- Davidson, T. R., et al. (2024). [Self-Recognition in Language
  Models](https://doi.org/10.18653/v1/2024.findings-emnlp.703).
- Hasan, M. N., & Hossain, M. A. (2026). [An Empirical Study of
  Output-to-Input Loops for Black-Box Backdoor Detection in Fine-Tuned
  Open-Weight LLMs](https://arxiv.org/abs/2608.11348).
- Kamoi, R., et al. (2024). [When Can LLMs Actually Correct Their Own
  Mistakes?](https://doi.org/10.1162/tacl_a_00713).
- Lindsey, J. (2026). [Emergent Introspective Awareness in Large Language
  Models](https://arxiv.org/abs/2601.01828).
- Liu, Z., et al. (2026). [Do LLMs Catch Their Own
  Mistakes?](https://doi.org/10.18653/v1/2026.findings-acl.86).
- Madaan, A., et al. (2023). [Self-Refine: Iterative Refinement with
  Self-Feedback](https://arxiv.org/abs/2303.17651).
- Madsen, A., Chandar, S., & Reddy, S. (2024). [Are self-explanations from
  Large Language Models
  faithful?](https://doi.org/10.18653/v1/2024.findings-acl.19).
- Shinn, N., et al. (2023). [Reflexion: Language Agents with Verbal
  Reinforcement Learning](https://arxiv.org/abs/2303.11366).
- Shumailov, I., et al. (2024). [AI models collapse when trained on recursively
  generated data](https://doi.org/10.1038/s41586-024-07566-y).
- Song, S., Hu, J., & Mahowald, K. (2025). [Language Models Fail to Introspect
  About Their Knowledge of Language](https://arxiv.org/abs/2503.07513).
- Xu, W., et al. (2024). [Pride and Prejudice: LLM Amplifies Self-Bias in
  Self-Refinement](https://doi.org/10.18653/v1/2024.acl-long.826).
