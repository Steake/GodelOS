# V9 beta: reliable conversation and bounded evolution

Runtime build 9.0.0-beta.1. Existing mind schema 8.0.0 is retained to preserve saved histories. The interface labels this release V9 beta. This is not the complete arbitrary-code self-evolution architecture.

## Failures addressed

* Model-output validation used to reject the whole reply when self-observation references were invalid. The runtime now preserves the exact raw output, delivers a complete reply, quarantines proposed cognitive updates, and records an engine episode so attention can move on. Strict validation remains available for experiments. Unsupported claims in a delivered reply are not certified as true.
* A complete top-level JSON reply can be recovered even when later metadata is malformed. Missing or unterminated reply text is never invented. Provider failures retain the input and produce a human-readable notice; no automatic repeated provider call is made.
* Chat submissions enter a persisted inbox. They wait behind a running inference and take precedence over the next idle cycle. A running inference is allowed to finish. Concurrent inbox additions do not invalidate an otherwise unchanged cognitive state. Composing holds new idle work for 30 seconds, refreshed on input. Browser drafting stops the local multi-cycle loop.
* Repetition previously used only object IDs. Recent title-token overlap now contributes to habituation, and duplicate candidate thoughts are not appended. This is lexical similarity, not a demonstrated semantic understanding of stagnation.
* Personality now has persisted warmth, playfulness, directness and reflectiveness, with reason-labelled changes limited to 0.03 per episode. Affect shapes an explicit expression profile for cadence, warmth, humour and imagery. These are implemented mechanisms; live-model prose variation has not yet been demonstrated.

## Executable evolution

Experiments → V9 beta · Self-modification lab:

1. Design and test requests a model-generated thesis, attention-policy expression and 2–20 authored tests.
2. A compiler validates a bounded arithmetic AST (63 nodes, depth 8; salience, need, affect and repeats). No arbitrary JavaScript is executed.
3. Authored tests and an independently implemented 80-case controller suite execute locally.
4. Eligibility requires all authored tests, at least 0.05 gain, a positive lower bootstrap bound and no regression in either controller task family.
5. An Ed25519-signed package contains the program hash, value constitution, evidence, parent hash and rollback target.
6. Deployment verifies signature, parent, current values and gate, then persists the program in the active attention controller. Rollback restores the predecessor. Human message selection remains an unconditional override.
7. Three-round mode designs, tests and deploys eligible candidates, feeding the previous result into the next design. It runs while the page is open, with a stop control and ten design calls per day.

Deployment here means activation of a bounded attention program within the existing agent. It does not deploy a new external website, patch arbitrary repository files, modify model weights, or support arbitrary generated testbed code. Those capabilities remain future work.

## Evidence and limits

62 automated tests pass, including queue precedence, raw-output preservation, malformed-metadata reply recovery, composing hold, ID-independent habituation, personality persistence, compiler limits, signatures, old-state upgrade, deployment and rollback. Browser verification exercised candidate design, gate display, deployment and rollback through the actual API with an explicitly synthetic provider.

The illustrative synthetic candidate improved the specified controller benchmark by 48.75 percentage points (bootstrap interval 38.75–60.00). This is a hand-written fixture against a constructed benchmark, NOT a DeepSeek research finding. The fixed suite is reused, so repeated feedback can overfit it; its bootstrap interval does not establish generalisation. The eligibility gate authorises only experimental controller deployment.

No live DeepSeek call was made in this pass. The provider interface is wired to the existing configured provider. No conclusion about consciousness, personality quality or long-horizon utility follows from these infrastructure tests.

## Next decisive experiment

Run paired real-model conversations from the same state, matching sampling parameters, with expression mapping on/off and repeated-theme handling on/off. Include frustration, positive evidence, social contact, contradiction and blocked investigation. Independently score conversational relevance, distinctive expressive variation, repetition and provenance errors. Retain all raw outputs, and add an unseen task family before broader autonomous promotion. Arbitrary code mutation needs an isolated execution service plus independently authored held-out behavioural tests.

## Reproduction

From deploy/netlify-sovereignty-lab:

    node --test tests/*.test.mjs
    node scripts/verify-build.mjs

From the repository root:

    python scripts/build_netlify_sovereignty_bundle.py --zip-output output/deploy/godelos-v9-beta-netlify.zip

The supplied V8 PDF remains historical. It does not describe these changes. Use this document for this beta.

## Dark mode

V9 beta includes a persistent light/dark workspace toggle. It uses `localStorage` key `godelos-theme` and respects `prefers-color-scheme: dark` when no choice exists. Dark mode covers the navigation rail, app bar, conversation surface, composer, suggestions, experiment panels, settings, access gate and status controls. The toggle is keyboard accessible and exposes `aria-pressed` state.

### V9.1 interface repair

The theme contract now covers the retained calibration, value, workbench,
independence and living-agent components. Legacy literal white surfaces and dark
text can no longer combine with the dark palette. Research grids and their
nested panels are explicitly shrinkable, collapse before they can exceed the
viewport, and clip accidental page-level horizontal overflow. The repair was
verified against the Value Lab, Calibration and Experiments screens in a live
browser preview.
