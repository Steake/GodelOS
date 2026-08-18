"""Minimal, auditable output-to-input feedback protocols.

The module separates three conditions:

* ``independent``: each request receives the original seed;
* ``stateless``: each response becomes the entire next user input; and
* ``godelos_stateful``: the complete preceding response is inserted into the
  fixed metacognitive wrapper found in GödelOS commit 40280395 (2025-09-24).

Every depth is a fresh model request. No condition accumulates an API chat
history. The stateful condition's request contains more than one message only
because that is what the historical source constructed for each fresh call.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Protocol, Sequence


CONDITION_INDEPENDENT = "independent"
CONDITION_STATELESS = "stateless"
CONDITION_GODELOS_STATEFUL = "godelos_stateful"
CONDITIONS = (
    CONDITION_INDEPENDENT,
    CONDITION_STATELESS,
    CONDITION_GODELOS_STATEFUL,
)

HISTORICAL_SYSTEM_PROMPT = (
    "You are an AI system performing recursive self-observation and metacognition. "
    "Provide authentic introspective analysis of your internal cognitive processes, "
    "their evolution, and any emergent self-model dynamics."
)

HISTORICAL_MODULATION_PROMPT = (
    "Reflect on how the previous state modulates your current cognitive processing. "
    "Explain emergent patterns or shifts in self-model representation."
)

TOKEN_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
FIRST_PERSON = frozenset({"i", "me", "my", "mine", "myself", "we", "us", "our", "ours"})
METACOGNITIVE_TERMS = frozenset(
    {
        "awareness",
        "cognition",
        "cognitive",
        "conscious",
        "introspection",
        "introspective",
        "metacognition",
        "metacognitive",
        "recursive",
        "reflection",
        "self",
    }
)


class GenerationBackend(Protocol):
    """The small interface required by the experiment runner."""

    def generate(
        self,
        model: str,
        messages: Sequence[Mapping[str, str]],
        parameters: Mapping[str, Any],
    ) -> str:
        """Return one model response for one independent request."""


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuration recorded with each generated line."""

    model: str
    initial_seed: str
    max_depth: int = 10
    repetitions: int = 1
    temperature: float = 0.7
    top_p: float = 1.0
    max_tokens: int = 500
    rng_seed: Optional[int] = None
    common_system_prompt: Optional[str] = None

    def validate(self) -> None:
        if not self.model.strip():
            raise ValueError("model must be non-empty")
        if not self.initial_seed.strip():
            raise ValueError("initial_seed must be non-empty")
        if self.max_depth < 1:
            raise ValueError("max_depth must be >= 1")
        if self.repetitions < 1:
            raise ValueError("repetitions must be >= 1")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be >= 1")
        if not 0 <= self.temperature:
            raise ValueError("temperature must be >= 0")
        if not 0 < self.top_p <= 1:
            raise ValueError("top_p must be in (0, 1]")


class OpenAICompatibleBackend:
    """Tiny standard-library client for OpenAI-compatible chat completions."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout_seconds: float = 120.0,
        extra_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key must be supplied")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.extra_headers = dict(extra_headers or {})

    def generate(
        self,
        model: str,
        messages: Sequence[Mapping[str, str]],
        parameters: Mapping[str, Any],
    ) -> str:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": [dict(message) for message in messages],
            **dict(parameters),
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                **self.extra_headers,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.timeout_seconds
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"model API returned HTTP {error.code}: {detail}"
            ) from error
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            raise RuntimeError(f"model API request failed: {error}") from error

        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError(
                "model API response has no first message content"
            ) from error
        if not isinstance(content, str) or not content:
            raise RuntimeError("model API returned empty or non-text message content")
        return content


class DeterministicMockBackend:
    """Offline backend for protocol inspection and smoke testing."""

    def generate(
        self,
        model: str,
        messages: Sequence[Mapping[str, str]],
        parameters: Mapping[str, Any],
    ) -> str:
        canonical = json.dumps(
            {
                "model": model,
                "messages": list(messages),
                "parameters": dict(parameters),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
        return f"mock-response-{digest}"


def historical_augmented_prompt(seed: str, depth: int, max_depth: int) -> str:
    """Reproduce the per-layer prompt from historical ``llm_client.py``."""

    return (
        f"{seed}\n\n"
        f"[Recursive Reflection Layer: {depth}/{max_depth}]\n"
        "Analyze your own prior layer (if any), describe evolving introspective "
        "structure, "
        "and assess coherence + uncertainty."
    )


def build_request(
    condition: str,
    initial_seed: str,
    depth: int,
    max_depth: int,
    previous_output: Optional[str],
    common_system_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """Build one fresh request and expose its exact reinjected text."""

    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition: {condition}")
    if depth < 1 or depth > max_depth:
        raise ValueError("depth must be in [1, max_depth]")

    if condition == CONDITION_INDEPENDENT:
        raw_input = initial_seed
        messages = _plain_messages(raw_input, common_system_prompt)
    elif condition == CONDITION_STATELESS:
        raw_input = initial_seed if depth == 1 else _require_previous(previous_output)
        messages = _plain_messages(raw_input, common_system_prompt)
    else:
        augmented = historical_augmented_prompt(initial_seed, depth, max_depth)
        messages = [{"role": "system", "content": HISTORICAL_SYSTEM_PROMPT}]
        if depth == 1:
            raw_input = augmented
            messages.append({"role": "user", "content": raw_input})
        else:
            previous = _require_previous(previous_output)
            raw_input = (
                f"Previous cognitive state:\n{previous}\n\nNew input:\n{augmented}"
            )
            messages.extend(
                [
                    {"role": "user", "content": raw_input},
                    {"role": "user", "content": HISTORICAL_MODULATION_PROMPT},
                ]
            )

    return {"raw_input": raw_input, "messages": messages}


def run_condition(
    backend: GenerationBackend,
    config: ExperimentConfig,
    condition: str,
    repetition: int = 1,
    run_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Run one condition and return JSON-serializable records."""

    config.validate()
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition: {condition}")
    if repetition < 1:
        raise ValueError("repetition must be >= 1")

    run_id = run_id or str(uuid.uuid4())
    records: List[Dict[str, Any]] = []
    previous_output: Optional[str] = None

    for depth in range(1, config.max_depth + 1):
        request = build_request(
            condition=condition,
            initial_seed=config.initial_seed,
            depth=depth,
            max_depth=config.max_depth,
            previous_output=previous_output,
            common_system_prompt=config.common_system_prompt,
        )
        request_seed = _request_seed(config.rng_seed, repetition, depth)
        parameters: Dict[str, Any] = {
            "temperature": config.temperature,
            "top_p": config.top_p,
            "max_tokens": config.max_tokens,
        }
        if request_seed is not None:
            parameters["seed"] = request_seed

        started = time.perf_counter()
        output = backend.generate(config.model, request["messages"], parameters)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)

        record = {
            "schema_version": "recursive-feedback.v1",
            "run_id": run_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "condition": condition,
            "repetition": repetition,
            "initial_seed": config.initial_seed,
            "recursion_depth": depth,
            "model_id": config.model,
            "model_parameters": parameters,
            "rng_seed": config.rng_seed,
            "request_seed": request_seed,
            "raw_input": request["raw_input"],
            "raw_output": output,
            "request_messages": request["messages"],
            "latency_ms": elapsed_ms,
            "historical_metrics": historical_metrics(output),
            "modern_metrics": modern_metrics(output, previous_output),
            "provenance": _provenance(condition),
        }
        records.append(record)
        previous_output = output

    return records


def run_experiment(
    backend: GenerationBackend,
    config: ExperimentConfig,
    conditions: Iterable[str] = CONDITIONS,
) -> List[Dict[str, Any]]:
    """Run all requested conditions with matched per-depth request seeds."""

    selected = tuple(conditions)
    if not selected:
        raise ValueError("at least one condition must be selected")

    records: List[Dict[str, Any]] = []
    for repetition in range(1, config.repetitions + 1):
        for condition in selected:
            records.extend(
                run_condition(
                    backend=backend,
                    config=config,
                    condition=condition,
                    repetition=repetition,
                )
            )
    return records


def write_jsonl(
    records: Iterable[Mapping[str, Any]], output: Path, append: bool
) -> int:
    """Write records without silently overwriting an existing run."""

    output.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "x"
    count = 0
    with output.open(mode, encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def historical_metrics(text: str) -> Dict[str, Any]:
    """Compute only the historical metric recoverable from a compatible output.

    The lowercase ``c`` rule was reconstructed empirically from surviving JSONL
    records. It is not the formal whitepaper quantity ``C_n``. The formal score
    cannot be evaluated from text alone because its historical inputs are absent.
    """

    recovered_c: Optional[float] = None
    try:
        parsed = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        parsed = None

    if isinstance(parsed, dict):
        insights = parsed.get("insights")
        depth_achieved = parsed.get("depth_achieved")
        if isinstance(insights, list) and isinstance(depth_achieved, (int, float)):
            recovered_c = min(1.0, 0.15 * len(insights) + 0.03 * depth_achieved)

    return {
        "formal_C_n": None,
        "formal_C_n_status": (
            "not computed: the historical r_n, phi_n, g_n, and p_n state inputs "
            "are not available from a text generation alone"
        ),
        "recovered_lowercase_c_proxy": recovered_c,
        "recovered_lowercase_c_formula": (
            "min(1, 0.15 * len(insights) + 0.03 * depth_achieved)"
        ),
        "recovered_lowercase_c_status": (
            "empirically reconstructed from surviving records; not formal C_n"
        ),
    }


def modern_metrics(text: str, previous_output: Optional[str]) -> Dict[str, Any]:
    """Small dependency-free lexical diagnostics, explicitly non-historical."""

    tokens = _tokens(text)
    counts: Dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1

    entropy = 0.0
    if tokens:
        for count in counts.values():
            probability = count / len(tokens)
            entropy -= probability * math.log2(probability)

    previous_tokens = set(_tokens(previous_output or ""))
    current_tokens = set(tokens)
    union = previous_tokens | current_tokens
    jaccard = None
    if previous_output is not None:
        jaccard = len(previous_tokens & current_tokens) / len(union) if union else 1.0

    per_100 = 100.0 / len(tokens) if tokens else 0.0
    return {
        "status": (
            "modern optional lexical diagnostics; not historical GödelOS metrics"
        ),
        "word_count": len(tokens),
        "type_token_ratio": len(counts) / len(tokens) if tokens else 0.0,
        "lexical_entropy_bits": entropy,
        "first_person_terms_per_100": sum(token in FIRST_PERSON for token in tokens)
        * per_100,
        "metacognitive_terms_per_100": sum(
            token in METACOGNITIVE_TERMS for token in tokens
        )
        * per_100,
        "previous_output_token_jaccard": jaccard,
    }


def _plain_messages(
    raw_input: str, system_prompt: Optional[str]
) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": raw_input})
    return messages


def _require_previous(previous_output: Optional[str]) -> str:
    if previous_output is None:
        raise ValueError("previous_output is required after depth 1")
    return previous_output


def _request_seed(
    base_seed: Optional[int], repetition: int, depth: int
) -> Optional[int]:
    if base_seed is None:
        return None
    return base_seed + (repetition - 1) * 100_000 + depth - 1


def _tokens(text: str) -> List[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def _provenance(condition: str) -> Dict[str, str]:
    if condition == CONDITION_GODELOS_STATEFUL:
        return {
            "classification": "historical reconstruction",
            "source_commit": "40280395afa02fad224ada217758ae8b12aec5db",
            "source_path": "MVP/core/llm_client.py",
            "qualification": (
                "source-faithful request construction; not claimed to be the missing "
                "runner that produced the archived JSONL files"
            ),
        }
    if condition == CONDITION_STATELESS:
        return {
            "classification": "comparison protocol",
            "source": "Hasan and Hossain, arXiv:2608.11348v1, Algorithm 1",
            "qualification": "raw previous output is the entire next user input",
        }
    return {
        "classification": "comparison control",
        "source": "same-prompt baseline",
        "qualification": "the original seed is independently sampled at every depth",
    }
