# GödelOS Workspace V10 — Netlify deployment

This package opens on **Conversation**. **Activity** makes the persistent
attention, imagination, memory, intention and self-observation loop inspectable.
Conversation enters that same loop. V10 adds paired light/dark themes, a live
input graphic, attention-score breakdowns, a position-revision ledger, saved
drafts and background-worker status, quota and recovery controls. V10.1 adds
incremental model output and an honest five-stage operation monitor: input,
context, provider stream, validation and atomic persistence. Streamed prose is
provisional; no autobiographical state changes until the complete structured
response passes validation.
Thoughts generated in one cycle can compete for attention in later cycles.
The living-agent view, workbench and earlier chambers remain available.
This is an experimental architecture for constructing a computational mind;
its self-descriptions are inspectable claims.

The DeepSeek key is used only inside a Netlify Function. Persistent agent state
is stored in a site-scoped, strongly consistent Netlify Blob using conditional
ETag writes. The browser receives neither the provider key nor direct provider
access.

## Deploy the complete app

Netlify Drop uploads static files without running a build. It does not deploy
this package's server-side chat by merely dropping the source folder.
Use the CLI (or Git-connected deployment) for the complete app:

1. Unzip `godelos-workspace-v10-netlify.zip`.
2. Open a terminal in the unzipped `netlify-sovereignty-lab` folder.
3. Run `npm ci`, then `npx netlify-cli login` and `npx netlify-cli link` to select
   your existing site (or `npx netlify-cli init` for a new site).
4. In **Project configuration → Environment variables**, add:
   - `DEEPSEEK_API_KEY`: your DeepSeek key.
   - `SOVEREIGNTY_ACCESS_TOKEN`: a long password of your choosing. This gates
     the dashboard and protects the provider spend and agent mutations.
5. Ensure both variables are available to **Functions**, then run
   `npx netlify-cli deploy --build --prod`.
6. Open the `netlify.app` URL. Enter the access token when prompted. It remains
   in that browser tab's session storage and is not written into the site files.

Optional variables are documented in `.env.example`. The deployed default model
is `deepseek-flash`. The UI separately labels the provider-returned model of
the last completion and the configured model for the next call. Change
`DEEPSEEK_MODEL` if the account exposes a different model alias.

To let the agent run bounded thought episodes without an open browser, also set:

- `AUTONOMY_ENABLED=true`
- `AUTONOMY_INTERVAL_MINUTES=15`
- `AUTONOMY_DAILY_CALL_LIMIT=24`

Existing site environment settings override these defaults. If your site still
specifies 360 minutes and four calls, change those values. After redeploying,
the desktop app bar must say **V10.1**, with the headline **A thought can become
a thread.** State on the same Netlify site is retained; V8 mind records migrate
in place. Mobile hides the compact build label to leave room for the controls.

Deployment reference: https://docs.netlify.com/deploy/create-deploys/

## Use the mind

Use **Think one cycle**, or select 3, 6 or 12 cycles and **Begin**. Attention
determines the mode. Talk to the agent while following intentions, imagined
objects, remembered events and proposed revisions. **Pause autonomous thought**
stops new idle cycles; chat remains available. One already-running call may
finish. Recent conversation reloads from saved evidence. **Download last cycle
evidence** includes exact prompts, provider output and state changes. An expired
call can be acknowledged and recovered without replaying it.

Background thought consists of scheduled discrete episodes. The app displays
social invitations. Proposed code and policy revisions remain candidates.
See `research/integrated-mind-v8/INTEGRATED_MIND_V8_RESULTS.md` for actual evidence.

## Use the workbench

1. Open **Experiment workbench** after connecting.
2. Choose **Agent-led**, enter a research question and select a round/task budget.
3. Click **Start self-directed experiment**. The agent designs, executes and
   critiques each round. Keep the tab open for steps to keep advancing.
4. Use **Pause**, **Run / resume** or **One step** to control the run.
5. Open any decision for its prompt, raw response and independent answer.
6. Ask the agent about the result, download the evidence, or fork the next test.

**Operator-led** mode lets you set the inherited policy, difficulty and seed.
Its **Dry run** option uses synthetic oracle responses and makes zero model calls.
Completed research persists in Netlify Blobs. Closing the tab stops further
requests after the current call; return and resume from the saved state.

Experiments currently use the executable three-period planning template. The
agent cannot silently invent new benchmark code or promote its live policy.
See `research/WORKBENCH_V5.md` for the method, limits and actual live results.

## Historical Adaptive Adversarial Benchmark Forge v4

The Benchmark Forge tab displays the new live pilot, power plan and promotion
status separately from historical v3 results. `research/` contains the runnable
Python forge, its methodology and collected v4 evidence. See `research/README.md`.
The forge is a separate research worker, not a long-running Netlify Function.
No identity-state policy from that benchmark has been promoted. V8's integrated
mind is an explicitly experimental architecture with a separate evidence record.

### Historical instrument view

Open **Benchmark Forge** in the navigation after connecting. Its five views explain
the test, the live evidence, an inspectable task and answer key, bounded diagnostic
commands, and the next engineering capability. In **Inspect a task**, choose a
source or transfer episode, compare plans, then reveal verification and the oracle
answer. Authentic but irrelevant evidence is distinguished from invalid signatures.

**Prepare a diagnostic** defaults to zero provider calls. Its live option generates
a command and explicit call budget; it does not launch a hidden background job.
Run that command from `research/`. Existing agent conversation remains available
in its original tab. The new view is read-only and cannot promote a candidate.

## V10 verification and diagnostic

See `WORKSPACE_V10.md` and `research/workspace-v10/RESULTS.md` for this build's
changes and retained evidence. `public/godelos-workspace-v10-report.pdf` is the
illustrated report. Screenshots are explicitly labelled synthetic UI verification;
provider-run records are kept separately. The earlier failed preflight is retained.

```bash
npm ci
npm test
npm run build
npm run dev
```

The dev command uses synthetic responses and in-memory state. It is for UI
verification, including the 390px frame at `/__qa/mobile`. It does not call DeepSeek.

To reproduce the six-arm diagnostic (fresh output directories are required):

```bash
node scripts/workspace-experiment.mjs --out new-fixture
# DEEPSEEK_API_KEY must be present in the shell environment for the next command.
node scripts/workspace-experiment.mjs --live --out new-provider-run
```

The default is 54 maximum calls: six arms, three scenario clusters, three phases
per branch. `--config path.json` accepts a JSON configuration; see
`research/workspace-v10/config.example.json`. Tasks and code hashes are sealed
before collection. Exact requests, raw responses, quarantines, failures and
derived scores are retained. This is an instrument diagnostic, not a powered
test of consciousness or identity-specific benefit. No policy promotion follows
from its scores. Existing workbench and controller-evolution rounds remain
browser-driven; scheduled background thinking uses the server worker.

## Historical V8 experiments

Two V8 engineering runs received 36 real DeepSeek completions. R1 applied 13
and rejected five; R2 applied all 18, including two disclosed closing-brace
repairs. The final observation-receipt interface has local tests; its additional
live diagnostic was blocked by automatic approval review before any completion
was received. 52 Node tests pass. Browser QA exercised synthetic interaction
and displayed actual R2 evidence in read-only mode. This pass did not deploy
to your Netlify account.

```bash
npm ci
npm test
npm run build
```

To run a fresh 18-call experiment with `DEEPSEEK_API_KEY` in the environment:

```bash
node scripts/live-mind.mjs new-mind-run
node scripts/analyse-mind.mjs new-analysis new-mind-run
```

For eight continuing episodes only, append `--cycles-only` to `live-mind.mjs`.
Both collection scripts refuse existing output directories. The optional
six-call observation diagnostic is:

```bash
node scripts/live-mind-observation.mjs new-mind-run/report.json new-observation-run
```

`npm run dev` is a synthetic UI preview. `npm run preview:evidence` is a
read-only view of packaged R2 records. Neither contacts DeepSeek.

From the GödelOS repository root, regenerate the curated seed, report copy,
manifest, and deployment ZIP with:

```bash
python scripts/build_netlify_sovereignty_bundle.py --zip-output output/deploy/godelos-workspace-v10-netlify.zip
```

To exercise Functions and Blobs locally, install the Netlify CLI and run
`netlify dev`. Supply environment variables through the CLI or a local ignored
`.env` file. Do not add a real `.env` file to the deployment archive.

## Runtime model

- `GET /api/health` is public and reports configuration booleans only.
- All state and mutation routes require `Authorization: Bearer <access token>`.
- `GET /api/snapshot` returns the current state and research results.
- `POST /api/chat` performs dialogue through the integrated mind.
- `POST /api/mind/cycle` advances one autonomous cognitive cycle.
- `POST /api/mind/control` persists the pause state.
- `GET /api/mind/history` restores the last 12 successful episodes.
- `GET /api/mind/evidence/:id` exposes an exact recorded attempt.
- `POST /api/mind/recover` acknowledges an expired attempt without replay.
- `POST /api/think` runs deliberation, associative reverie, affective
  integration, drift, or heterodox exploration.
- `POST /api/value-profile` creates an immutable candidate without activating it.
- Netlify Blobs stores one fixed state key. Clients cannot select arbitrary Blob
  keys. Research jobs and campaigns use separate server-managed keys.
- Every deployed transition extends a SHA-256 event chain.
- Writes use Blob ETags. Concurrent mutation returns HTTP 409 instead of silently
  overwriting a newer state.
- `SOVEREIGNTY_DAILY_CALL_LIMIT` defaults to 250 model calls per UTC day.
- `FORGE_DAILY_CALL_LIMIT` defaults to 128 research calls per UTC day.
- `/api/forge/jobs` creates and lists saved diagnostics; job routes provide
  advance, pause, resume, raw response inspection, review and export.
- `/api/forge/campaigns` creates and lists agent-led campaigns; campaign routes
  provide advance, pause, resume and complete evidence export.

## Evidence boundary

The seed contains the curated state, the completed 120-call DeepSeek calibration,
and the v3 chamber result: 96 branch phases plus two scientific reviews and one
patch proposal. It excludes SQLite databases, raw transcripts, signing material,
provider credentials, and unrelated repository material. New dialogue and
cognition events are persisted in the site's Blob store.

V8 raw transcripts are packaged separately under `research/integrated-mind-v8`;
they are not automatically substituted for the live site's agent state.

The web runtime executes the v5 planning diagnostic and agent-led iteration.
Its previous code-patch evaluation and signed production-promotion machinery
remain separate. The full
protocol compiler, disposable patch evaluation and signed promotion controller
run from the repository CLI. The deployed UI reports their authenticated result;
it cannot bypass the promotion gate or mutate production code.
