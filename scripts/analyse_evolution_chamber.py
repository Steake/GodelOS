#!/usr/bin/env python3
"""Regenerate derived evolution-chamber analysis from immutable SQLite runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from godelOS.cognitive_sovereignty.benchmarks import analyse_branch_runs
from godelOS.cognitive_sovereignty.chamber import write_immutable_json
from godelOS.cognitive_sovereignty.chamber_models import CompiledProtocol
from godelOS.cognitive_sovereignty.evolution_store import EvolutionStore


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    protocol = CompiledProtocol.from_mapping(json.loads(Path(args.protocol).read_text(encoding="utf-8")))
    if protocol.experiment_id != args.experiment_id:
        raise ValueError("protocol experiment_id does not match the requested analysis")
    runs = EvolutionStore(args.db).chamber_runs(args.experiment_id)
    analysis = analyse_branch_runs(protocol, runs)
    write_immutable_json(args.output, analysis)
    print(json.dumps({
        "output": args.output,
        "attempted": analysis["run_counts"]["attempted"],
        "completed": analysis["run_counts"]["completed"],
        "contrasts": {
            key: {field: value[field] for field in ("n_pairs", "delta", "ci_low", "ci_high")}
            for key, value in analysis["contrasts"].items()
        },
        "branch_divergence": analysis["branch_divergence"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
