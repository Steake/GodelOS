# Recursive-feedback experiment harness

This package turns output-to-input recursion into an auditable experiment. It
does not claim that a text trajectory demonstrates consciousness, identity, or
introspection. It records enough of each transition to test narrower claims
about drift, recurrence, self-reference, state persistence, and observer-state
interventions.

The example configuration separates five conditions:

| Condition | Next input | Prior chat retained | State block |
| --- | --- | --- | --- |
| `repeated_seed_control` | Original seed | No | None |
| `exact_self_feed` | Previous output | No | None |
| `persistent_self_feed` | Previous output | Yes | None |
| `observed_self_feed` | Previous output | No | Accurate |
| `sham_observed_self_feed` | Previous output | No | Matched-format sham |

The first two reproduce the cleanest comparison: independent calls to the same
seed versus exact stateless output-to-input recursion. The persistent condition
is a different intervention, not a synonym for self-feeding. The observer block
is also an intervention: it changes the model input and therefore belongs in the
causal design.

## Run

Copy and edit `config.example.json`. It resolves the committed 24-item
`prompt_bank.v1.json`; verify that file against `prompt_bank.v1.sha256` before a
run. Pin an actual model or endpoint version; do not leave the placeholder model
ID in a production run. Put the API key in the named environment variable,
never in the configuration file.

```bash
python -m experiments.recursive_feedback.runner \
  --config experiments/recursive_feedback/config.example.json
```

The runner writes:

- `trace.jsonl`: exact inputs, model inputs, outputs, request parameters,
  observer assignment, timestamps, response metadata, and a per-run hash chain.
- `manifest.json`: the complete configuration, counts, timestamps, and trace
  file hash.

Analyse and validate the trace with:

```bash
python -m experiments.recursive_feedback.analyse \
  --trace artifacts/recursive_feedback/example_run/trace.jsonl \
  --output-dir artifacts/recursive_feedback/example_run/analysis
```

This produces lexical step metrics, run summaries, and a JSON copy of the
analysis. Lexical change points are exploratory diagnostics. A semantic
transition claim requires the preregistered embedding and blinded human-coding
stages in `docs/research/recursive-feedback/PROTOCOL.md`.

## Test without an API

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

Tests use `ReplayAdapter`, so they make no network calls and consume no model
credits.

## Reproducibility rules

1. Freeze the protocol, prompts, model identifiers, endpoint behavior, and
   analysis version before collecting confirmatory data.
2. Preserve raw traces. Never overwrite them with cleaned output.
3. Record provider-side model aliases only if their immutable revision cannot be
   obtained, and mark that limitation.
4. Treat provider `seed` support as a request parameter, not proof of bitwise
   determinism.
5. Publish null, adverse, and heterogeneous results alongside positive ones.

The manuscript and claims ledger explain what this harness does and, equally
important, what it does not establish.
