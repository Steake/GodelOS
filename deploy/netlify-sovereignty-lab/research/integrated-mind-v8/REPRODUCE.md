# Reproduce the V8 evidence from this ZIP

Run these commands from `netlify-sovereignty-lab` after unzipping.

```bash
npm ci
npm test
npm run build
node scripts/analyse-mind.mjs analysis-reproduced research/integrated-mind-v8/integrated-mind-v8-live research/integrated-mind-v8/integrated-mind-v8-live-r2
python -m pip install -r research/integrated-mind-v8/requirements.txt
python research/integrated-mind-v8/generate_report.py --analysis analysis-reproduced/analysis.json --screenshot research/integrated-mind-v8/godelos-integrated-mind-v8-report-view.jpg --output report-reproduced.pdf --figures figures-reproduced
```

The Python pins record the versions used for this pass. The required report
fonts and their licence are bundled. Python 3.11+ is recommended. Node 20+
runs the deployed code. `npm run preview:evidence` opens the actual saved
state in a read-only local preview; `npm run dev` uses synthetic completions.

For a new real experiment, put `DEEPSEEK_API_KEY` in the process environment:

```bash
DEEPSEEK_MAX_TOKENS=3500 node scripts/live-mind.mjs new-run
node scripts/analyse-mind.mjs new-analysis new-run
```

This issues at most 18 provider requests and refuses an existing output
directory. Append `--cycles-only` for the eight-episode trajectory alone.
The final kernel includes observation receipts and priority revision added
after R2. Therefore a new live run is a new experiment, not a byte-identical
replay of R2. R1 and R2 raw records are never edited by analysis.

The six-call `live-mind-observation.mjs` diagnostic was prepared but received
no completion in this session because automatic approval review blocked its
saved-checkpoint transfer. See its `execution-blocked.json`; do not treat it
as a completed comparison.

For production, use Netlify CLI or a Git-connected build, as described in the
root README. The package's `public` directory alone is insufficient for chat
and autonomous Functions.
