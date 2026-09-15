# V8.2 workspace redesign

Replaces V8.1 presentation with a five-destination operator interface: Conversation, Activity, Experiments, Archive and Settings. The existing authenticated state and experiment engines are reused. This release does not change the cognitive kernel or experimental scoring.

Conversation is a dedicated full-height surface with a stable composer, draft-filling suggestions, Enter to send, Shift+Enter for newlines, visible call progress, disabled send during generation, and draft restoration on failure. Activity contains thought controls, focus and state inspection. Experiments explains Ask / Compare / Learn, keeps optional run settings out of the primary form, and collapses configuration when results are active. Archive retains older instruments and the research PDF. Settings retains values, model provenance and event-chain status. The header exposes the last reported model and links to its details. Responsive CSS changes the navigation rail into bottom navigation on narrow screens.

Visual direction: restrained plum accent, neutral tonal surfaces, typography-led hierarchy, separate task panes. Material navigation guidance was consulted as a reference, not imported as a framework. No Bootstrap dependency was added.

Validation: 52 Node tests passed. Browser checks exercised all primary destinations, a suggested prompt submitted with Enter, disabled send while pending, actual provider-label update using the synthetic fixture, operator-led configuration, a zero-provider-call diagnostic completing 8/8 phases, and restoration of its saved results. Browser preview responses are explicitly labelled synthetic; no new live-model research findings are claimed. Mobile breakpoints are implemented but no mobile-device browser verification was performed in this pass.

Reproduce package from repository root:
python scripts/build_netlify_sovereignty_bundle.py --zip-output output/deploy/godelos-studio-v8.2-netlify.zip

Validate from deploy/netlify-sovereignty-lab:
node --test tests/*.test.mjs
node scripts/verify-build.mjs

The packaged V8 PDF remains a historical research report and contains the earlier interface. Interface revision is V8.2; cognitive kernel remains 8.0.0.
