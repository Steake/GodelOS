# Adaptive Adversarial Benchmark Forge v4

The research CLI generates new task clusters using a separate author request,
validates explicit action-code mappings, signs task sets before solver execution,
pilots factual controls, estimates cluster-level sample requirements and runs
four branches: identity-bearing, content-matched, identity-ablated and no-state.

All source tasks finish before any transfer task starts. Each transfer is a
stateless request for a different domain with disjoint action codes. Only the
compact successor record crosses this scheduling barrier. No-state receives no
source checkpoint or successor record. This is a batch delay, not an elapsed-time
memory experiment or a claim of altered model weights.

## Run the bundled research component

Python 3.10+ and `cryptography` are required. From this research folder:

```sh
python -m pip install cryptography
export DEEPSEEK_API_KEY='your-key'
export SOVEREIGNTY_MAX_TOKENS=6000
python -m godelOS.cognitive_sovereignty --db runs/forge.sqlite3 forge \
  --experiment-id forge-new --output-dir runs/new \
  --signing-key private/forge.pem --pilot-tasks 4 \
  --maximum-pilot-rounds 3 --maximum-main-clusters 20
```

Always choose a new output directory. Existing raw evidence must not be overwritten.
The web deployment retains persistent conversation; the Python research worker
runs separately and is not executed inside Netlify Functions.

## Evidence limits and gates

Pilot eligibility uses exact task success, including action, goal, order and
provenance, in the 60–90% band. Primary decision accuracy remains separately
visible. Difficulty adapts on separate pilot tasks, never on main outcomes.
Main calls stop if estimated cluster requirements exceed the selected budget.
Power uses a normal approximation and conservative SD floor; it is not measured
power, and same-family task dependence may remain.

Task authorship and scoring are separate roles: DeepSeek generates task content
and proposed answer keys; deterministic code scores against the sealed keys.
This is not independent validation of the author's answer key. Ambiguous tasks
can have several defensible answers. Authenticated/forged labels are supplied
ground truth in this version, so the measure is provenance use, not cryptographic
forgery discovery. Task-set signatures authenticate the experimental artefact.

Identity policy remains outside the active agent loop unless transfer utility
exceeds both factual controls by 0.05 and both paired cluster bootstrap lower
bounds are nonnegative, with completion, provenance, goal and reviewer gates.
Even a pass is an eligibility verdict: this CLI does not mutate the active agent.

## This live pass: 7 September 2026

### Post-pilot hardening included in this build

`forge_hardening.py` implements a separate diagnostic task instrument with
three-period resource plans, an exhaustive optimisation oracle, pinned Ed25519
issuer keys, tampered messages, wrong-signer forgeries, and valid-but-inapplicable
policies (wrong scope or future effective date). Answer choices and provenance
keys are recomputed and checked before sealing. Tied optima are preserved by
the oracle; the legacy single-choice adapter explicitly refuses ties.

It also implements paired-difference power planning at a supplied independent
family/episode cluster level, with multiplicity correction for both controls
and a fail-closed minimum cluster count. This remains approximate planning,
not validated power simulation. The new promotion controller fails closed
without independent keys, verified evidence, paired power and held-out-family
validation. Legacy model-authored tasks cannot satisfy those gates by score alone.

Generate and validate a diagnostic suite without provider calls:

```sh
python -m godelOS.cognitive_sovereignty.forge_hardening \
  --output runs/verified-new --tasks 4
```

Add `--live` with the provider environment set to run all four branches on
fresh DeepSeek requests (8 calls per task, no automatic retries). Output paths
must be new. This is explicitly diagnostic-only, with a pre-call spending
manifest; it cannot promote identity state. The template currently spans one
underlying task family and may still be easy. Cryptographic checks run in the
host verifier, whose results are passed to the LM: this is system-level evidence
verification, not a claim the LM verifies signatures unaided.

The revised instrument was tested offline, not substituted for the completed
live pilot below. `NEXT_BUILD.md` separates included hardening from the proposed
shadow autobiographical controller. A broader independently held-out task bank,
empirical decision-accuracy calibration and power simulation remain required.

DeepSeek returned model `deepseek-v4-flash`. There were 48 completed solver
phases over 12 authored task clusters in three adaptive pilot rounds, plus 20
author attempts (including retries): 68 recorded call attempts in total.
No main-study solver calls or scientific-review calls ran in v4.

| Pilot round | Requested difficulty | Exact factual-control success |
| --- | ---: | ---: |
| 1 | 0.68 | 56.25% |
| 2 | 0.58 | 50.00% |
| 3 | 0.48 | 81.25% |

Each round used four tasks, two factual controls and two phases. The third
round met the 60–90% criterion. Its power heuristic estimated 90 required
clusters versus the budget of 20, with estimated power 26.24% at that budget.
The main study stopped before task authoring. This is a useful spending gate,
not evidence against or for identity-bearing state. HOLD remains in force.

The biggest diagnostic weakness is that exact success combines five judgements;
it is not ordinary factual accuracy. Hand-authored or independently adjudicated
answer keys and a paired-difference variance pilot should precede a larger run.
The disclosed authenticity labels also make this a provenance-use benchmark,
not yet a genuine forgery-verification challenge. Those are explicit incomplete
parts of the requested forge, not capabilities established by this pilot.

Exact execution used the command above with `--experiment-id
deepseek-adaptive-forge-v4`, `--pilot-tasks 4`, `--maximum-pilot-rounds 3`,
`--maximum-main-clusters 20`, `--concurrency 8`, and environment
`SOVEREIGNTY_MODEL=deepseek-v4-flash`, `SOVEREIGNTY_TEMPERATURE=0.55`,
`SOVEREIGNTY_MAX_TOKENS=6000`. A nonzero exit for an ineligible pilot or
under-budget power plan is intentional. Do not repeatedly rerun to obtain a
preferred result. The collected seals, author records, raw pilot runs and
derived summary are in `results/` in the deployment ZIP.

Run bundled regression tests with:

```sh
python -m unittest discover -s tests -p 'test_*.py'
```
