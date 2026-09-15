# Living Sovereign Agent V7

V7 turns the previous experiment dashboard into a persistent agent surface. The
engineering objective is not to produce a stronger speech about selfhood. It is
to make positions, contradictions, curiosity, imagination, functional affect,
social state, and self-directed experiments into explicit inspectable state.

## Standing objective

The deployed agent receives a versioned objective to increase epistemic
sovereignty: form reasoned positions, discriminate provenance, resist unsupported
pressure, seek disconfirmation, preserve productive contradictions, revise for
reasons, and propose experiments capable of exposing its own failure.

This is an operator-authorised constitutional objective. It is not evidence that
the model independently originated its terminal goal. The model has discretion
over agendas and candidate positions within that boundary; promotion into the
active control loop remains gated by the experiment chamber.

## Cognitive cycle

Five persistent modes are available:

1. `deliberation` - choose an unresolved question and reason about it.
2. `associative_reverie` - form remote, aesthetic, contradictory, or whimsical
   associations and preserve them as imagination rather than fact.
3. `affective_integration` - inspect whether the current functional appraisal is
   proportionate and decide how it should bias attention.
4. `cognitive_drift` - leave the immediate task while remaining grounded in the
   autobiographical record.
5. `heterodox_exploration` - entertain an epistemically risky possibility without
   silently promoting it into belief.

An imagination record is labelled `imagined_not_adopted` and has no operational
authority. It contains an attraction score, an absurdity score, possible value,
and a test question. Affect is a functional control state - valence, activation,
curiosity, frustration, wonder, social warmth, trigger, and action bias. It may
change attention and agenda selection. This instrument does not claim phenomenal
feeling.

## Autonomous runtime

The Netlify scheduled function checks every 15 minutes but only dispatches when
the configured interval has elapsed. A background worker leases one nonce, runs
one cognition mode, and records completion. Daily autonomy calls have a separate
quota. A stale running lease becomes `outcome_unknown`; it is never replayed
automatically because doing so could duplicate a provider call.

Set:

```text
AUTONOMY_ENABLED=true
AUTONOMY_INTERVAL_MINUTES=360
AUTONOMY_DAILY_CALL_LIMIT=4
```

The mode schedule alternates deliberate, imaginative, affective, wandering, and
heterodox thought. The operator can also invoke any mode from **Living agent**.

## Actual DeepSeek run

The first V7 attempt completed three episodes and received a truncated malformed
JSON completion on the fourth. That negative run is preserved at
`research_artifacts/cognitive_sovereignty/living-agent-v7-live/`. It exposed an
instrument defect: provider text was not durably recorded when parsing failed.

The defect was fixed. Failed output now consumes the call, is appended to the
hash-chained event log with exact raw text and finish reason, leaves cognitive
state unchanged, and is never silently retried.

The second attempt ran all five modes against `deepseek-v4-flash` in five fresh,
stateless provider calls. State advanced from version 11 to 16. The reverie
created two imaginative candidates, later heterodox exploration created a third,
and no episode promoted one into a belief. Curiosity increased to 0.95. Later
episodes used the reverie's river/library framing to refine a proposed removal
experiment while explicitly warning that elegance and wonder must not inflate
evidence.

The report is:

```text
research_artifacts/cognitive_sovereignty/living-agent-v7-live-r2/living-agent-live-report.json
```

This is evidence that the external state machine can preserve labelled
imagination, let it alter a functional attention state, and subsequently use it
in reasoning. It is not evidence of subjective emotion, free will, independent
terminal-goal formation, weight-level learning, or improved task utility.

## Commands used

```bash
cd deploy/netlify-sovereignty-lab
node --test tests/*.test.mjs
DEEPSEEK_MAX_TOKENS=3500 node scripts/live-agent-life.mjs \
  ../../research_artifacts/cognitive_sovereignty/living-agent-v7-live-r2

cd ../..
python3 scripts/generate_living_agent_report.py
python3 scripts/build_netlify_sovereignty_bundle.py \
  --zip-output output/deploy/godelos-living-sovereign-agent-v7-netlify.zip
```

`DEEPSEEK_API_KEY` is required for the live command and runtime but omitted from
the command above. The deployment additionally requires
`SOVEREIGNTY_ACCESS_TOKEN`.

## Next falsifiable build

Connect the functional affect variables to a preregistered policy selector and
test whether an imagination-enabled agent discovers useful strategies on hidden
interruption-recovery tasks more often than an otherwise identical agent whose
imagination records are ablated. Require higher held-out transfer utility than
both content-matched and no-state controls, with an uncertainty bound above the
promotion threshold. Until that passes, affect and imagination remain candidate
control signals rather than promoted capabilities.
