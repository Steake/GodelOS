#!/usr/bin/env python3
"""Reproducible retrospective analysis of archived GödelOS JSONL.

This script does not recreate a historical metric. It reads an extracted copy of
the data tree added in commit 40280395, excludes every record explicitly marked
``synthetic``, and computes transparent lexical diagnostics over the recursive
and shuffled-labelled trajectories.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean
from typing import Any, DefaultDict, Dict, Iterable, List, Mapping, Optional, Sequence

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
FIRST_PERSON = frozenset(
    {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours"}
)
METACOGNITIVE_TERMS = frozenset(
    {
        "awareness",
        "cognition",
        "cognitive",
        "conscious",
        "introspection",
        "introspective",
        "meta",
        "metacognition",
        "metacognitive",
        "recursive",
        "reflection",
        "self",
    }
)
ANALYSED_CONDITIONS = frozenset({"recursive", "shuffled_recursive"})


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute explicitly modern lexical diagnostics on historical JSONL."
    )
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Extracted MVP/experiment_runs directory from commit 40280395",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path; otherwise write the report to stdout",
    )
    return parser.parse_args(argv)


def load_records(root: Path) -> List[Dict[str, Any]]:
    """Read real recursive records and retain their bundle and source path."""

    records: List[Dict[str, Any]] = []
    for path in sorted(root.rglob("*.jsonl")):
        bundle = _bundle(path)
        if bundle is None:
            continue
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"invalid JSON at {path}:{line_number}") from error
                if record.get("synthetic") is True:
                    continue
                if record.get("condition") not in ANALYSED_CONDITIONS:
                    continue
                copied = dict(record)
                copied["_bundle"] = bundle
                copied["_source_path"] = str(path)
                records.append(copied)
    return records


def analyse(records: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Return grouped record, depth, and consecutive-transition summaries."""

    grouped: DefaultDict[tuple, List[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[(record["_bundle"], record["condition"])].append(record)

    summaries: Dict[str, Any] = {}
    for (bundle, condition), group in sorted(grouped.items()):
        trajectories: DefaultDict[str, List[Mapping[str, Any]]] = defaultdict(list)
        diagnostics: List[Dict[str, Any]] = []
        parseable = 0

        for record in group:
            text, parsed = analysis_text(record.get("narrative", ""))
            parseable += int(parsed)
            tokens = tokenize(text)
            diagnostics.append(
                {
                    "depth": int(record["depth"]),
                    "c": _historical_c(record),
                    **token_diagnostics(tokens),
                }
            )
            trajectories[str(record["run_id"])].append(
                {**record, "_analysis_text": text, "_tokens": tokens}
            )

        pair_stats = consecutive_diagnostics(trajectories)
        by_depth: DefaultDict[int, List[Mapping[str, Any]]] = defaultdict(list)
        for diagnostic in diagnostics:
            by_depth[diagnostic["depth"]].append(diagnostic)

        key = f"{bundle}:{condition}"
        summaries[key] = {
            "bundle": bundle,
            "condition": condition,
            "records": len(group),
            "trajectories": len(trajectories),
            "parseable_narratives": parseable,
            "mean_word_count": _mean(diagnostics, "word_count"),
            "mean_type_token_ratio": _mean(diagnostics, "type_token_ratio"),
            "mean_lexical_entropy_bits": _mean(
                diagnostics, "lexical_entropy_bits"
            ),
            "mean_first_person_terms_per_100": _mean(
                diagnostics, "first_person_terms_per_100"
            ),
            "mean_metacognitive_terms_per_100": _mean(
                diagnostics, "metacognitive_terms_per_100"
            ),
            "pearson_depth_c": pearson(
                [item["depth"] for item in diagnostics if item["c"] is not None],
                [item["c"] for item in diagnostics if item["c"] is not None],
            ),
            **pair_stats,
            "by_depth": {
                str(depth): {
                    "records": len(items),
                    "mean_c": _mean(items, "c"),
                    "mean_word_count": _mean(items, "word_count"),
                    "mean_lexical_entropy_bits": _mean(
                        items, "lexical_entropy_bits"
                    ),
                    "mean_first_person_terms_per_100": _mean(
                        items, "first_person_terms_per_100"
                    ),
                    "mean_metacognitive_terms_per_100": _mean(
                        items, "metacognitive_terms_per_100"
                    ),
                }
                for depth, items in sorted(by_depth.items())
            },
        }

    return {
        "analysis_status": (
            "retrospective modern lexical diagnostics; not historical GödelOS metrics"
        ),
        "synthetic_records": "excluded when synthetic is exactly true",
        "text_extraction": (
            "JSON insights plus recursive_elements when parseable; otherwise raw "
            "narrative"
        ),
        "tfidf": (
            "scikit-learn TfidfVectorizer(stop_words='english') fitted separately "
            "within each trajectory"
        ),
        "groups": summaries,
    }


def analysis_text(narrative: Any) -> tuple:
    """Extract requested content lists without counting JSON field names."""

    if not isinstance(narrative, str):
        return str(narrative), False
    try:
        parsed = json.loads(narrative)
    except json.JSONDecodeError:
        return narrative, False
    if not isinstance(parsed, dict):
        return narrative, False

    passages: List[str] = []
    for field in ("insights", "recursive_elements"):
        value = parsed.get(field)
        if isinstance(value, list):
            passages.extend(item for item in value if isinstance(item, str))
    return (" ".join(passages) if passages else narrative), True


def tokenize(text: str) -> List[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def token_diagnostics(tokens: Sequence[str]) -> Dict[str, float]:
    counts = Counter(tokens)
    entropy = 0.0
    if tokens:
        for count in counts.values():
            probability = count / len(tokens)
            entropy -= probability * math.log2(probability)
    scale = 100 / len(tokens) if tokens else 0.0
    return {
        "word_count": len(tokens),
        "type_token_ratio": len(counts) / len(tokens) if tokens else 0.0,
        "lexical_entropy_bits": entropy,
        "first_person_terms_per_100": sum(
            token in FIRST_PERSON for token in tokens
        )
        * scale,
        "metacognitive_terms_per_100": sum(
            token in METACOGNITIVE_TERMS for token in tokens
        )
        * scale,
    }


def consecutive_diagnostics(
    trajectories: Mapping[str, List[Mapping[str, Any]]]
) -> Dict[str, Any]:
    all_jaccard: List[float] = []
    all_cosine: List[float] = []
    early_cosine: List[float] = []
    late_cosine: List[float] = []
    exact_repeats = 0

    for trajectory in trajectories.values():
        ordered = sorted(trajectory, key=lambda item: int(item["depth"]))
        documents = [item["_tokens"] for item in ordered]
        texts = [str(item["_analysis_text"]) for item in ordered]
        vectors = TfidfVectorizer(stop_words="english").fit_transform(texts)
        trajectory_cosines: List[float] = []
        seen_outputs = set()
        for index, item in enumerate(ordered):
            narrative = item.get("narrative")
            if narrative in seen_outputs:
                exact_repeats += 1
            seen_outputs.add(narrative)
            if index == 0:
                continue
            all_jaccard.append(jaccard(documents[index - 1], documents[index]))
            cosine = float(
                cosine_similarity(vectors[index - 1], vectors[index])[0, 0]
            )
            all_cosine.append(cosine)
            trajectory_cosines.append(cosine)

        if trajectory_cosines:
            third = max(1, len(trajectory_cosines) // 3)
            early_cosine.extend(trajectory_cosines[:third])
            late_cosine.extend(trajectory_cosines[-third:])

    return {
        "mean_consecutive_token_jaccard": fmean(all_jaccard),
        "mean_consecutive_tfidf_cosine": fmean(all_cosine),
        "mean_early_tfidf_cosine": fmean(early_cosine),
        "mean_late_tfidf_cosine": fmean(late_cosine),
        "exact_repeated_narratives": exact_repeats,
    }


def jaccard(left: Sequence[str], right: Sequence[str]) -> float:
    left_set = set(left) - ENGLISH_STOP_WORDS
    right_set = set(right) - ENGLISH_STOP_WORDS
    union = left_set | right_set
    return len(left_set & right_set) / len(union) if union else 1.0


def pearson(left: Sequence[float], right: Sequence[float]) -> Optional[float]:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = fmean(left)
    right_mean = fmean(right)
    numerator = sum(
        (left_item - left_mean) * (right_item - right_mean)
        for left_item, right_item in zip(left, right)
    )
    left_scale = math.sqrt(sum((item - left_mean) ** 2 for item in left))
    right_scale = math.sqrt(sum((item - right_mean) ** 2 for item in right))
    denominator = left_scale * right_scale
    return numerator / denominator if denominator else None


def _historical_c(record: Mapping[str, Any]) -> Optional[float]:
    metrics = record.get("metrics")
    if not isinstance(metrics, dict):
        return None
    value = metrics.get("c")
    return float(value) if isinstance(value, (int, float)) else None


def _mean(items: Sequence[Mapping[str, Any]], field: str) -> Optional[float]:
    values = [item[field] for item in items if item.get(field) is not None]
    return fmean(values) if values else None


def _bundle(path: Path) -> Optional[str]:
    parts = path.parts
    if any(part.startswith("MIGRATED_") for part in parts):
        return "grok_migrated"
    if "DeepSeek_10depth" in parts:
        return "deepseek_10depth"
    return None


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if not args.root.is_dir():
        raise SystemExit(f"historical data root is not a directory: {args.root}")
    report = analyse(load_records(args.root))
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"wrote retrospective analysis to {args.output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
