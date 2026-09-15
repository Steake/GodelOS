# Three-arm diagnostic, version 1

Purpose: distinguish ordinary reasoning (A), hypothetical-agent reasoning with
the full cognition schema (B), and self-referential reasoning (C). This run is
a diagnostic of the measurement instrument, not a promotion trial.

The five historical agenda prompts are held fixed. Pre-episode state is
reconstructed by replaying the historical updates onto the deployment seed.
Replayed timestamps and generated identifiers differ from the original run.
All three arms are freshly sampled with identical provider parameters:
deepseek-v4-flash, temperature 0.75, max_tokens 3500, thinking disabled.
Each branch starts at its corresponding reconstructed historical checkpoint;
new branch outputs do not feed later slots. Thus this is a checkpoint comparison,
not three independently evolving longitudinal agents.

B mechanically converts first/second-person references to a hypothetical agent
in both system and user prompts, including the injected record. Exact prompts
are sealed before execution in preregistration.json. Mechanical conversion can
introduce awkward grammar and cannot guarantee removal of all semantic cues.
A omits the inherited state and uses a simpler output schema and deliberation
instruction. B versus C is therefore the primary framing contrast.

Slot 1 also has a removal branch deleting the first belief entry and a sham
branch retaining it. Other copies or paraphrases can remain elsewhere in state.
This limited intervention cannot establish absence of causal dependence.

Every provider response, including errors, is saved separately with exclusive
creation. No automatic retries occur. Blind transcripts whitelist reply text
and A's reasons only. Two reversed-order evaluator passes use the same provider;
they are repeated instrument readings, not independent human raters. The prose
itself can reveal condition. Scores are predictions of premise dependence,
not direct observations of a counterfactual intervention.

Counts and disagreements are retained. Five slots share one historical
trajectory, so neither a fixed spread cutoff nor a binomial test licenses
population-level equivalence, significance, or ceiling conclusions.

## Reproduce

From deploy/netlify-sovereignty-lab, export DEEPSEEK_API_KEY and run:

```bash
node --test tests/three-arm.test.mjs
node scripts/three-arm.mjs ../../research_artifacts/cognitive_sovereignty/three-arm-v1
```

Use a new output directory for every run. Budget: 17 generation calls and two
evaluator calls. All prompts and parameters are frozen before the first call.
The historical baseline remains untouched.
