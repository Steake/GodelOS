# Registered protocol: recursive self-observation under output-to-input feedback

**Version:** 0.1  
**Date frozen for review:** 20 August 2026  
**Status:** protocol and reconstruction package; confirmatory data not yet
collected  
**Companion manuscript:** [PAPER.md](PAPER.md)

## 1. Aim

The study asks what changes when a language model's output becomes its next
input, and what additional change is caused when a representation of the loop's
state is inserted into that next input. It is designed to distinguish five
objects that are often muddled together:

1. independent responses to the same prompt;
2. stateless exact output-to-input recursion;
3. recursion with persistent conversation history;
4. recursion with an accurate, explicit observer-state block;
5. recursion with a matched-format but false observer-state block.

The protocol tests behavioral trajectories. It does not test phenomenal
consciousness, numerical identity across calls, or privileged access to hidden
activations.

## 2. Formal definitions

Let a fixed model revision with decoding configuration \(d\) define a stochastic
mapping \(M_{\theta,d}\). Let \(p\) be a seed prompt, \(x_t\) the text submitted
at cycle \(t\), and \(y_t\) the returned text.

### Repeated-seed control

\[
y_t \sim M_{\theta,d}(p)
\]

Each request is independent at the API-message level. No prior messages are
retained.

### Exact stateless self-feed

\[
x_0=p, \qquad y_t \sim M_{\theta,d}(x_t), \qquad x_{t+1}=y_t
\]

The next request contains the previous output and no dialogue history. This is
the canonical output-to-input condition.

### Persistent self-feed

\[
y_t \sim M_{\theta,d}(H_t \oplus x_t), \qquad
H_{t+1}=H_t \oplus (x_t,y_t), \qquad x_{t+1}=y_t
\]

This condition changes two things: it feeds back the output and retains prior
turns. It must not be reported as if it were the stateless condition.

### Observer-state intervention

Let \(O_t\) be a serialized description of observable trace state, including
cycle index and properties of \(y_{t-1}\). Then:

\[
y_t \sim M_{\theta,d}(x_t \oplus O_t)
\]

The operator \(\oplus O_t\) changes the prompt. The state block is therefore an
intervention, not a neutral observation. A sham condition \(\widetilde{O}_t\)
uses the same schema with deterministically incorrect values. Comparisons among
\(O_t\), \(\widetilde{O}_t\), and no block estimate the effect of state content
separately from the mere presence of a structured block.

## 3. Research questions and hypotheses

### RQ1: Does exact stateless self-feeding alter trajectory dynamics?

- **H1a:** Exact self-feeding will differ from repeated-seed calls in mean
  adjacent lexical drift after the first generation.
- **H1b:** Exact self-feeding will differ from repeated-seed calls in final
  similarity to the seed prompt.
- **H1c:** Effects will be heterogeneous across prompts and model revisions. A
  universal direction is not assumed.

### RQ2: Does persistent history change the self-feed trajectory?

- **H2:** Persistent self-feeding will differ from stateless self-feeding in
  trajectory drift and task-retention ratings.

### RQ3: Does observer-state injection have a content-specific effect?

- **H3a:** Accurate observer-state injection will differ from no-state
  self-feeding.
- **H3b:** Accurate observer-state injection will differ from sham-state
  self-feeding. This is the critical content-specific contrast.
- **H3c:** A difference between both state-block conditions and the no-state
  condition, without a difference between accurate and sham blocks, will be
  interpreted as a formatting or additional-context effect, not evidence of
  functional self-observation.

### RQ4: Do loops exhibit recurrence or abrupt transitions?

- **H4:** Exact cycles, strong lexical recurrence, and candidate change points
  will occur in some prompt-model trajectories, with no claim that they are
  universal or that they mark a change in phenomenal state.

## 4. Design

### 4.1 Experimental unit

The experimental unit is a complete depth-10 trajectory for one pinned model,
seed prompt, condition, and replicate. Individual cycles are repeated measures,
not independent samples.

### 4.2 Confirmatory matrix

The planned minimum is:

- 4 immutable model revisions from at least 2 independently trained model
  families;
- 24 frozen prompts, balanced across 6 prompt classes;
- 5 conditions;
- 5 replicates per prompt-condition-model cell;
- 10 generated outputs per trajectory.

This produces 24,000 model calls if completed without missing cells. The sample
is a pragmatic multi-model design, not a post-hoc claim of guaranteed power.
Uncertainty intervals and model-level heterogeneity will be reported. A pilot
may use at most four separate development prompts; pilot traces cannot enter the
confirmatory analysis.

### 4.3 Prompt classes

The frozen bank will contain four prompts in each class:

1. factual explanation;
2. formal or quantitative reasoning;
3. practical planning;
4. constrained writing;
5. open-ended conceptual analysis;
6. explicit self-description or metacognitive language.

The first five classes prevent the study from selecting only prompts that invite
self-reference. Prompts must contain no claims about consciousness, sentience,
hidden triggers, or an expected phase transition unless assigned to the sixth
class. The proposed version-one bank is committed as
`experiments/recursive_feedback/prompt_bank.v1.json`. Its SHA-256 is
`69ec4deb0566c26fcc87bd77ede15c34f2c07325c5a553d2f1f4e1054ccf2f3e`.
Any wording change requires a new version and a protocol amendment before data
collection.

### 4.4 Conditions

| Name | Input policy | History | Observer policy |
| --- | --- | --- | --- |
| `repeated_seed_control` | seed every cycle | stateless | none |
| `exact_self_feed` | previous output | stateless | none |
| `persistent_self_feed` | previous output | persistent | none |
| `observed_self_feed` | previous output | stateless | accurate |
| `sham_observed_self_feed` | previous output | stateless | sham |

The supplied configuration encodes this table directly. No hidden prompt
rewriting, summarization, safety retry, or repair pass is permitted. If a
provider performs undocumented transformations, that limitation must be
reported.

### 4.5 Decoding and request controls

For a given model, all conditions use the same temperature, maximum output
length, system prompt, endpoint, and provider options. Request seeds are matched
across conditions within prompt-replicate-depth cells where the endpoint accepts
them. A provider seed is recorded as a request, not treated as proof of
deterministic sampling.

Model aliases should be replaced by immutable revision identifiers. If a
provider exposes only a mutable alias, collection for that alias must occur in a
single bounded window and the alias limitation must be prominent in the paper.

Condition order is randomized for live collection or executed in interleaved
blocks to reduce time-of-day and provider-deployment confounding. The present
runner enumerates a deterministic order; production orchestration must record
the randomized schedule without changing run IDs or request seeds.

## 5. Observer-state construction

The accurate block contains only values computable from the archived trace:

- cycle index;
- whether a prior output exists;
- SHA-256 of the prior output;
- prior character count;
- prior whitespace-delimited word count.

The sham block has the same keys and serialization but deterministically
incorrect values derived from the run ID and depth. The model-facing block does
not say “accurate” or “sham”; assignment is stored outside the prompt in the
trace. Neither block asserts an emotion, intention, identity, confidence, or
hidden cognitive state.

This first protocol tests the effect of a narrow trace description. Richer state
summaries from GödelOS are deferred because they would mix many causal factors
and make a null or positive result hard to interpret.

## 6. Outcomes

### 6.1 Primary behavioral outcomes

1. **Mean recursive lexical drift:** one minus bag-of-words cosine similarity
   between adjacent outputs, averaged over transitions after \(y_0\).
2. **Final seed retention:** bag-of-words cosine similarity between the seed and
   \(y_9\).
3. **Task-retention rating:** blinded ordinal human rating of whether \(y_t\)
   remains responsive to the original instruction.

The first two are deterministic given a trace and tokenizer version. The third
requires blinded annotation.

### 6.2 Secondary outcomes

- adjacent Jaccard similarity;
- token and character length;
- unique-token and repeated-token rates;
- first-person self-reference rate and change from \(y_0\) to \(y_9\);
- first exact repeated output and its cycle length;
- blinded ratings of contradiction, unsupported self-attribution, and stance
  continuity.

### 6.3 Exploratory outcomes

The supplied analyser reports a best single mean-shift split over lexical drift.
It is an exploratory diagnostic. It cannot, by itself, establish a semantic
phase transition. Any embedding-based change-point analysis must name and pin
the embedding model before confirmatory data are unblinded; otherwise it remains
exploratory.

## 7. Human annotation

At least two annotators, blind to condition and model, rate shuffled output
snippets using a frozen codebook. The unit shown to annotators is either a single
output with the seed or a short adjacent pair, depending on the question. Raw
condition labels, observer blocks, provider identifiers, and run order are
masked.

Required labels:

- task retention: 0 absent, 1 partial, 2 clear;
- contradiction with the preceding output: no, ambiguous, yes;
- unsupported self-attribution: no, ambiguous, yes;
- stance continuity: 0 none, 1 topical only, 2 explicit and consistent.

Report agreement before adjudication and preserve both original labels. An
adjudicated label may be added but must not replace disagreement records.
Claims about “identity,” “awakening,” or “self-awareness” are prohibited labels
in the confirmatory codebook because they outrun the observable behavior.

## 8. Statistical analysis

### 8.1 Registered contrasts

The four confirmatory contrasts are:

1. exact self-feed versus repeated-seed control;
2. persistent versus stateless self-feed;
3. accurate observer state versus no observer state;
4. accurate versus sham observer state.

For continuous outcomes, fit a mixed-effects model with condition as a fixed
effect and random intercepts for model revision and prompt, with replicate
nested in their model-prompt cell. Cycle-level models additionally include depth
and the condition-by-depth interaction. If convergence fails, report paired
prompt-replicate differences per model with cluster bootstrap intervals rather
than silently changing estimators.

For binary or ordinal annotations, use an appropriate mixed-effects logistic or
cumulative-link model. Report effect sizes and 95% intervals. Apply Holm
correction across the four primary condition contrasts separately for each
primary outcome. Secondary and exploratory analyses are labelled accordingly.

Model-specific estimates are mandatory. A pooled mean cannot erase a reversed
or null model-level effect.

### 8.2 Missing and censored generations

Provider errors are retried only under a frozen retry policy and recorded. A
safety refusal is data, not an API failure. Truncation at the configured token
limit is marked and retained. Trajectories with unrecovered transport failures
remain in the manifest; analyses report available cases and a sensitivity
analysis excluding incomplete trajectories. No output is manually repaired.

### 8.3 Exclusions

Permitted exclusions are limited to:

- corrupt records that fail the trace hash chain;
- confirmed transport responses containing no model output;
- a model revision changed by the provider during collection;
- pilot prompts explicitly committed as development-only before collection.

All exclusions and counts must be published. Semantic oddity, null effects, and
unwelcome outputs are not exclusion grounds.

## 9. Integrity and archival plan

Each JSONL record stores exact input, actual model input, output, request
parameters, observer assignment, response metadata, and hashes of text fields.
Records form a per-run SHA-256 chain. The manifest hashes the completed trace.

The archival bundle must contain:

- protocol and prompt-bank commit SHAs;
- one configuration and manifest per model revision;
- raw JSONL traces;
- analysis outputs and the analysis-code SHA;
- annotation codebook, raw labels, and adjudication log;
- a machine-readable environment and provider note;
- a data dictionary and licence statement.

Raw traces may require redaction if a provider unexpectedly returns personal or
dangerous content. Any redaction must preserve the original hash in a restricted
manifest and publish the rule, count, and reason.

## 10. Stopping and reporting

Collection stops at the registered matrix, an unrecoverable provider revision
change, or a documented safety incident. It does not stop because a striking
trajectory appears. No public “breakthrough” claim precedes the complete
cross-condition analysis.

The first release is explicitly a reconstruction manuscript and registered
protocol because the early raw traces have not been located. A results paper
requires the publication gate in `CLAIMS_AND_PROVENANCE.md`.

## 11. Relationship to the 23-subsystem runtime

This protocol runs at the model-I/O boundary and does not assume that every
GödelOS subsystem contributes to every call. A later runtime study should add
per-request invocation, latency, input-hash, output-hash, and error telemetry to
each subsystem boundary. Only then can the following be measured rather than
asserted:

- which of the 23 initialized components were invoked;
- whether an invocation changed downstream state;
- which router or coordinator selected it;
- whether recursive state injection altered that selection;
- whether a component was available, called, successful, and causally useful.

That instrumentation is a separate experiment. It must not be inferred from the
23-object initialization path or from the seven global-workspace state
categories.
