#!/usr/bin/env python3
"""Command-line entry point for the recursive-feedback experiment."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Optional, Sequence

from recursive_feedback import (
    CONDITIONS,
    DeterministicMockBackend,
    ExperimentConfig,
    OpenAICompatibleBackend,
    run_experiment,
    write_jsonl,
)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run independent, stateless, and historical GödelOS feedback conditions."
        )
    )
    parser.add_argument("--seed", required=True, help="Initial seed prompt")
    parser.add_argument(
        "--model",
        default=os.environ.get("LLM_MODEL"),
        help="Model identifier (or set LLM_MODEL)",
    )
    parser.add_argument("--depth", type=int, default=10, help="Maximum recursive depth")
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=500)
    parser.add_argument("--rng-seed", type=int)
    parser.add_argument(
        "--condition",
        action="append",
        choices=CONDITIONS,
        dest="conditions",
        help="Repeat to select conditions; defaults to all three",
    )
    parser.add_argument(
        "--common-system-prompt",
        help=(
            "Optional fixed system prompt for independent/stateless conditions. "
            "The historical stateful condition always uses its recovered prompt."
        ),
    )
    parser.add_argument(
        "--backend", choices=("openai-compatible", "mock"), default="openai-compatible"
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
        help="OpenAI-compatible API root (or set LLM_BASE_URL)",
    )
    parser.add_argument(
        "--api-key-env",
        default="LLM_API_KEY",
        help="Environment-variable name containing the API key",
    )
    parser.add_argument(
        "--extra-headers-env",
        default="LLM_EXTRA_HEADERS_JSON",
        help="Optional JSON object of provider-specific HTTP headers",
    )
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to an existing JSONL file; otherwise existing paths are rejected",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    model = args.model
    if args.backend == "mock":
        model = model or "deterministic-mock"
        backend = DeterministicMockBackend()
    else:
        if not model:
            raise SystemExit("--model or LLM_MODEL is required")
        api_key = os.environ.get(args.api_key_env)
        if not api_key:
            raise SystemExit(f"API credential not found in {args.api_key_env}")
        extra_headers = _extra_headers(args.extra_headers_env)
        backend = OpenAICompatibleBackend(
            api_key=api_key,
            base_url=args.base_url,
            timeout_seconds=args.timeout,
            extra_headers=extra_headers,
        )

    config = ExperimentConfig(
        model=model,
        initial_seed=args.seed,
        max_depth=args.depth,
        repetitions=args.repetitions,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        rng_seed=args.rng_seed,
        common_system_prompt=args.common_system_prompt,
    )
    records = run_experiment(
        backend=backend,
        config=config,
        conditions=args.conditions or CONDITIONS,
    )
    count = write_jsonl(records, args.output, append=args.append)
    print(f"wrote {count} records to {args.output}")
    return 0


def _extra_headers(environment_name: str) -> Dict[str, str]:
    raw = os.environ.get(environment_name)
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as error:
        raise SystemExit(f"{environment_name} is not valid JSON: {error}") from error
    if not isinstance(parsed, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in parsed.items()
    ):
        raise SystemExit(f"{environment_name} must be a JSON object of string headers")
    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
