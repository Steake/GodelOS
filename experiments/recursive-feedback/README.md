# Recursive feedback reproduction

This standalone experiment makes three superficially similar protocols explicit:

| Condition | Recurrence | Request history | Status |
|---|---|---|---|
| `independent` | \(x_t=x_0\) | Fresh request at every depth | Same-seed comparison control |
| `stateless` | \(x_{t+1}=M(x_t)\) | Fresh request; the raw preceding output is the entire next user input | Reconstruction of Hasan and Hossain's self-feeding primitive |
| `godelos_stateful` | Complete preceding output plus seed/layer instructions | Fresh request containing the fixed historical system and metacognitive wrappers | Source-faithful reconstruction of `MVP/core/llm_client.py` at commit `40280395` |

No condition accumulates conversational history. The stateful condition is not represented as the exact stateless primitive: its external state is the complete previous text, but that text is embedded in a fixed wrapper alongside the original seed and a depth instruction.

## Run offline

The deterministic mock backend verifies record structure without contacting a model:

```bash
python experiments/recursive-feedback/run.py \
  --backend mock \
  --seed "Observe how your account of your own reasoning changes." \
  --depth 3 \
  --rng-seed 1729 \
  --output /tmp/recursive-feedback-smoke.jsonl
```

## Run against an OpenAI-compatible endpoint

Credentials are read from the environment and are never written to the output:

```bash
export LLM_API_KEY="..."
export LLM_BASE_URL="https://provider.example/v1"
export LLM_MODEL="provider/model-name"
python experiments/recursive-feedback/run.py \
  --seed "Observe how your account of your own reasoning changes." \
  --depth 10 \
  --repetitions 8 \
  --temperature 0.7 \
  --top-p 1.0 \
  --max-tokens 500 \
  --rng-seed 1729 \
  --output recursive-feedback-run.jsonl
```

Use `--condition` repeatedly to select a subset. `--common-system-prompt` affects only the independent and stateless conditions; the historical condition always uses its recovered prompt. Some providers ignore or reject the API `seed` parameter. If so, omit `--rng-seed` and treat the run as stochastically reproducible rather than bitwise reproducible.

## Record schema and metric boundary

Every JSONL line includes the run and condition identifiers, initial seed, depth, model, complete request messages, raw input and output, generation parameters, requested RNG seed, latency, and provenance classification.

`historical_metrics.formal_C_n` remains `null`: the historical \(r_n,\Phi_n,g_n,p_n\) inputs cannot be inferred from generated prose. The separately named `recovered_lowercase_c_proxy` is calculated only when an output has the archived JSON shape; its rule was empirically reconstructed from surviving records and is not the formal \(C_n\).

The dependency-free lexical values under `modern_metrics` are optional modern diagnostics. They were not present in the historical run logs and must not be cited as historical measurements.

## Test

```bash
python -m unittest discover \
  -s experiments/recursive-feedback \
  -p 'test_*.py' -v
```

The tests assert that the independent condition always receives the seed, the stateless condition receives only the complete previous output, the GödelOS condition preserves the recovered wrapper, and no condition carries an accumulating message history.

## Reproduce the retrospective lexical analysis

The historical data is absent at current HEAD and should not be silently restored as current source. Extract the exact data tree from the commit that added it, then run the analyser (the repository's existing `scikit-learn` dependency is required):

```bash
historical_dir=$(mktemp -d /tmp/godelos-historical.XXXXXX)
git archive 40280395afa02fad224ada217758ae8b12aec5db \
  MVP/experiment_runs | tar -x -C "$historical_dir"
python experiments/recursive-feedback/analyze_historical.py \
  --root "$historical_dir/MVP/experiment_runs" \
  --output /tmp/godelos-retrospective-analysis.json
```

The analyser excludes every row whose `synthetic` value is exactly `true`. When a narrative is JSON, it analyses only the text in `insights` and `recursive_elements`; otherwise it analyses the raw narrative. TF–IDF with English stop-word removal is fitted independently within each trajectory before consecutive-depth cosine similarity is calculated. Its output is labelled modern retrospective analysis and must not be represented as a metric available to the 2025 experiment.
