"""Dependency-light analysis for recursive-feedback JSONL traces."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean
from typing import Any, Iterable, Mapping, Sequence

from .runner import SCHEMA_VERSION, verify_record_hash


TOKEN_PATTERN = re.compile(r"\b[\w']+\b", flags=re.UNICODE)
FIRST_PERSON_TERMS = {
    "i",
    "i'd",
    "i'll",
    "i'm",
    "i've",
    "me",
    "mine",
    "my",
    "myself",
    "we",
    "we'd",
    "we'll",
    "we're",
    "we've",
    "our",
    "ours",
    "ourselves",
    "us",
}


def tokenize(text: str) -> list[str]:
    """Return a stable, case-folded lexical tokenization."""

    return [match.group(0).casefold() for match in TOKEN_PATTERN.finditer(text)]


def jaccard_similarity(left: Sequence[str], right: Sequence[str]) -> float:
    """Set-based lexical Jaccard similarity."""

    left_set = set(left)
    right_set = set(right)
    if not left_set and not right_set:
        return 1.0
    union = left_set | right_set
    return len(left_set & right_set) / len(union)


def cosine_similarity(left: Sequence[str], right: Sequence[str]) -> float:
    """Bag-of-words cosine similarity."""

    left_counts = Counter(left)
    right_counts = Counter(right)
    if not left_counts and not right_counts:
        return 1.0
    if not left_counts or not right_counts:
        return 0.0
    dot = sum(
        count * right_counts.get(token, 0)
        for token, count in left_counts.items()
    )
    left_norm = math.sqrt(sum(count * count for count in left_counts.values()))
    right_norm = math.sqrt(
        sum(count * count for count in right_counts.values())
    )
    return dot / (left_norm * right_norm)


def self_reference_rate(tokens: Sequence[str]) -> float:
    """Fraction of lexical tokens that are first-person terms."""

    if not tokens:
        return 0.0
    return sum(token in FIRST_PERSON_TERMS for token in tokens) / len(tokens)


def repeated_token_rate(tokens: Sequence[str]) -> float:
    """Fraction of token occurrences beyond the first occurrence."""

    if not tokens:
        return 0.0
    return (len(tokens) - len(set(tokens))) / len(tokens)


def detect_change_point(values: Sequence[float]) -> dict[str, float | int] | None:
    """Return the best single mean-shift split and normalized SSE gain.

    This is an exploratory lexical statistic, not a semantic phase-transition
    detector.  The protocol requires semantic and human-coded measures before a
    substantive change-point claim can be made.
    """

    if len(values) < 4:
        return None

    def squared_error(segment: Sequence[float]) -> float:
        mean = fmean(segment)
        return sum((value - mean) ** 2 for value in segment)

    baseline = squared_error(values)
    candidates = []
    for split in range(2, len(values) - 1):
        score = squared_error(values[:split]) + squared_error(values[split:])
        candidates.append((score, split))
    best_score, best_split = min(candidates)
    gain = 0.0 if baseline == 0 else (baseline - best_score) / baseline
    return {
        "split_after_depth": best_split - 1,
        "normalized_sse_gain": gain,
    }


def read_trace(path: str | Path) -> list[dict[str, Any]]:
    """Read a trace and fail on hash-chain or schema violations."""

    records: list[dict[str, Any]] = []
    previous_hash_by_run: dict[str, str | None] = {}
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError(f"line {line_number}: record must be an object")
            if record.get("schema_version") != SCHEMA_VERSION:
                raise ValueError(
                    f"line {line_number}: unsupported schema_version "
                    f"{record.get('schema_version')!r}"
                )
            if not verify_record_hash(record):
                raise ValueError(f"line {line_number}: invalid record_sha256")
            run_id = record.get("run_id")
            if not isinstance(run_id, str):
                raise ValueError(f"line {line_number}: missing run_id")
            expected_parent = previous_hash_by_run.get(run_id)
            if record.get("parent_record_sha256") != expected_parent:
                raise ValueError(
                    f"line {line_number}: broken parent_record_sha256 chain"
                )
            previous_hash_by_run[run_id] = record["record_sha256"]
            records.append(record)
    if not records:
        raise ValueError("trace contains no records")
    return records


def _cycle_length(outputs: Sequence[str], index: int) -> int | None:
    for previous_index in range(index - 1, -1, -1):
        if outputs[previous_index] == outputs[index]:
            return index - previous_index
    return None


def analyse_records(
    records: Iterable[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Compute preregistered lexical step metrics and run summaries."""

    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["run_id"])].append(record)

    step_rows: list[dict[str, Any]] = []
    run_rows: list[dict[str, Any]] = []
    for run_id, run_records in sorted(grouped.items()):
        ordered = sorted(run_records, key=lambda item: int(item["depth"]))
        depths = [int(item["depth"]) for item in ordered]
        if depths != list(range(len(ordered))):
            raise ValueError(f"run {run_id}: depths must be contiguous from zero")
        outputs = [str(item["output_text"]) for item in ordered]
        output_tokens = [tokenize(output) for output in outputs]
        seed_tokens = tokenize(str(ordered[0]["seed_prompt"]))
        adjacent_drifts: list[float] = []
        cycle_depth: int | None = None
        cycle_length: int | None = None

        for index, record in enumerate(ordered):
            tokens = output_tokens[index]
            previous_tokens = output_tokens[index - 1] if index else seed_tokens
            adjacent_cosine = cosine_similarity(previous_tokens, tokens)
            adjacent_drift = 1.0 - adjacent_cosine
            adjacent_drifts.append(adjacent_drift)
            current_cycle_length = _cycle_length(outputs, index)
            if current_cycle_length is not None and cycle_depth is None:
                cycle_depth = index
                cycle_length = current_cycle_length
            condition = record["condition"]
            step_rows.append(
                {
                    "run_id": run_id,
                    "condition": condition["name"],
                    "input_policy": condition["input_policy"],
                    "history_policy": condition["history_policy"],
                    "observer_policy": condition["observer_policy"],
                    "prompt_id": record["prompt_id"],
                    "replicate": record["replicate"],
                    "depth": index,
                    "character_count": len(outputs[index]),
                    "token_count": len(tokens),
                    "unique_token_rate": (
                        len(set(tokens)) / len(tokens) if tokens else 0.0
                    ),
                    "repeated_token_rate": repeated_token_rate(tokens),
                    "self_reference_rate": self_reference_rate(tokens),
                    "adjacent_jaccard": jaccard_similarity(
                        previous_tokens, tokens
                    ),
                    "adjacent_cosine": adjacent_cosine,
                    "adjacent_drift": adjacent_drift,
                    "seed_cosine": cosine_similarity(seed_tokens, tokens),
                    "exact_cycle_length": current_cycle_length,
                }
            )

        first = ordered[0]
        condition = first["condition"]
        change_point = detect_change_point(adjacent_drifts)
        self_reference_values = [
            self_reference_rate(tokens) for tokens in output_tokens
        ]
        run_rows.append(
            {
                "run_id": run_id,
                "condition": condition["name"],
                "input_policy": condition["input_policy"],
                "history_policy": condition["history_policy"],
                "observer_policy": condition["observer_policy"],
                "prompt_id": first["prompt_id"],
                "replicate": first["replicate"],
                "observed_depth": len(ordered),
                "initial_generation_drift": adjacent_drifts[0],
                "mean_adjacent_drift": fmean(adjacent_drifts),
                "mean_recursive_drift": (
                    fmean(adjacent_drifts[1:])
                    if len(adjacent_drifts) > 1
                    else None
                ),
                "max_adjacent_drift": max(adjacent_drifts),
                "final_seed_cosine": cosine_similarity(
                    seed_tokens, output_tokens[-1]
                ),
                "initial_self_reference_rate": self_reference_values[0],
                "final_self_reference_rate": self_reference_values[-1],
                "self_reference_delta": (
                    self_reference_values[-1] - self_reference_values[0]
                ),
                "first_exact_cycle_depth": cycle_depth,
                "first_exact_cycle_length": cycle_length,
                "change_point_after_depth": (
                    change_point["split_after_depth"] if change_point else None
                ),
                "change_point_sse_gain": (
                    change_point["normalized_sse_gain"]
                    if change_point
                    else None
                ),
            }
        )
    return step_rows, run_rows


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_analysis(
    trace_path: str | Path,
    output_dir: str | Path,
) -> tuple[Path, Path, Path]:
    """Validate a trace, compute metrics, and write machine-readable outputs."""

    records = read_trace(trace_path)
    step_rows, run_rows = analyse_records(records)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    step_path = destination / "step_metrics.csv"
    run_path = destination / "run_summary.csv"
    analysis_path = destination / "analysis.json"
    _write_csv(step_path, step_rows)
    _write_csv(run_path, run_rows)
    analysis_path.write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "trace": str(trace_path),
                "record_count": len(records),
                "run_count": len(run_rows),
                "metric_scope": "lexical and exact-cycle diagnostics",
                "step_metrics": step_rows,
                "run_summaries": run_rows,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return step_path, run_path, analysis_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and analyse a recursive-feedback JSONL trace."
    )
    parser.add_argument("--trace", required=True, help="Path to trace.jsonl")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory for CSV and JSON analysis outputs",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = write_analysis(args.trace, args.output_dir)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
