# V8.1 interface update

Conversation and current focus are the primary working surface. Six state panels use native expandable details. Research and settings navigation is expandable; existing tools remain available. A plain-language guide explains interaction, exploration and controlled intervention. Cobalt and white replace the dark neon palette across the existing asset styles.

Model attribution: authenticated snapshots expose model_status.configured (the next requested model) separately from model_status.last_response (provider-reported model and response metadata from a recorded completion). Seed experiment model labels are never used as live attribution. Existing records without this metadata display an explicit absence until a new completion is recorded. This change does not rewrite historical results.

Validation: 52 Node tests pass, including assertions that the provider-reported model differs from configured model and survives a subsequent snapshot. Browser verification exercised a synthetic thought cycle, confirmed the distinct labels, expanded research navigation and opened the workbench. No paid provider calls or research reruns were performed for this interface update.

Build: python scripts/build_netlify_sovereignty_bundle.py --zip-output output/deploy/godelos-integrated-mind-v8.1-netlify.zip

The bundled V8 PDF describes the earlier research run and earlier interface. The cognitive kernel remains version 8.0.0; this is interface revision 8.1.
