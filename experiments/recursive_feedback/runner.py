"""Run preregistered recursive-feedback experiments.

The runner deliberately keeps the experimental intervention visible.  Exact
self-feeding, repeated-prompt controls, persistent history, and observer-state
injection are separate configuration fields rather than hidden prompt logic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol, Sequence


SCHEMA_VERSION = "1.0"
INPUT_POLICIES = {"seed", "previous_output"}
HISTORY_POLICIES = {"stateless", "persistent"}
OBSERVER_POLICIES = {"none", "accurate", "sham"}


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    """Hash UTF-8 text using SHA-256."""

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_hash(value: Mapping[str, Any]) -> str:
    """Hash a mapping using stable JSON encoding."""

    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256_text(encoded)


@dataclass(frozen=True)
class Condition:
    """One explicit feedback-loop condition."""

    name: str
    input_policy: str
    history_policy: str = "stateless"
    observer_policy: str = "none"

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("condition.name must not be empty")
        if self.input_policy not in INPUT_POLICIES:
            raise ValueError(
                f"unsupported input_policy {self.input_policy!r}; "
                f"expected one of {sorted(INPUT_POLICIES)}"
            )
        if self.history_policy not in HISTORY_POLICIES:
            raise ValueError(
                f"unsupported history_policy {self.history_policy!r}; "
                f"expected one of {sorted(HISTORY_POLICIES)}"
            )
        if self.observer_policy not in OBSERVER_POLICIES:
            raise ValueError(
                f"unsupported observer_policy {self.observer_policy!r}; "
                f"expected one of {sorted(OBSERVER_POLICIES)}"
            )
        if self.input_policy == "seed" and self.history_policy != "stateless":
            raise ValueError(
                "the repeated-seed control must be stateless; persistent "
                "history would make requests non-independent"
            )

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Condition":
        condition = cls(
            name=str(value["name"]),
            input_policy=str(value["input_policy"]),
            history_policy=str(value.get("history_policy", "stateless")),
            observer_policy=str(value.get("observer_policy", "none")),
        )
        condition.validate()
        return condition


@dataclass(frozen=True)
class ExperimentConfig:
    """Complete experiment configuration."""

    endpoint: str
    api_key_env: str
    model: str
    prompts: tuple[str, ...]
    conditions: tuple[Condition, ...]
    output_dir: str = "artifacts/recursive_feedback"
    depth: int = 10
    replicates: int = 3
    temperature: float = 0.7
    max_tokens: int = 512
    seed: int = 1729
    timeout_seconds: int = 120
    system_prompt: str = ""
    extra_request_fields: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.endpoint.startswith(("http://", "https://")):
            raise ValueError("endpoint must be an HTTP(S) URL")
        if not self.api_key_env.strip():
            raise ValueError("api_key_env must name an environment variable")
        if not self.model.strip():
            raise ValueError("model must not be empty")
        if not self.prompts or any(not prompt.strip() for prompt in self.prompts):
            raise ValueError("prompts must contain at least one non-empty string")
        if not self.conditions:
            raise ValueError("conditions must not be empty")
        for condition in self.conditions:
            condition.validate()
        if len({condition.name for condition in self.conditions}) != len(
            self.conditions
        ):
            raise ValueError("condition names must be unique")
        if self.depth < 1:
            raise ValueError("depth must be at least 1")
        if self.replicates < 1:
            raise ValueError("replicates must be at least 1")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")
        if self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be at least 1")
        reserved = {"messages", "model", "temperature", "max_tokens", "seed"}
        overlap = reserved.intersection(self.extra_request_fields)
        if overlap:
            raise ValueError(
                "extra_request_fields cannot override controlled fields: "
                + ", ".join(sorted(overlap))
            )

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, Any],
        *,
        base_dir: str | Path | None = None,
    ) -> "ExperimentConfig":
        raw_prompts = value.get("prompts")
        if raw_prompts is None:
            prompt_file = value.get("prompt_file")
            if not isinstance(prompt_file, str) or not prompt_file.strip():
                raise ValueError("provide either prompts or prompt_file")
            prompt_path = Path(base_dir or ".") / prompt_file
            prompt_payload = json.loads(prompt_path.read_text(encoding="utf-8"))
            if not isinstance(prompt_payload, list):
                raise ValueError("prompt_file root must be a JSON array")
            raw_prompts = [
                item["text"] if isinstance(item, dict) else item
                for item in prompt_payload
            ]
        if not isinstance(raw_prompts, (list, tuple)):
            raise ValueError("prompts must be a JSON array")
        config = cls(
            endpoint=str(value["endpoint"]),
            api_key_env=str(value.get("api_key_env", "OPENAI_API_KEY")),
            model=str(value["model"]),
            prompts=tuple(str(prompt) for prompt in raw_prompts),
            conditions=tuple(
                Condition.from_mapping(condition)
                for condition in value["conditions"]
            ),
            output_dir=str(
                value.get("output_dir", "artifacts/recursive_feedback")
            ),
            depth=int(value.get("depth", 10)),
            replicates=int(value.get("replicates", 3)),
            temperature=float(value.get("temperature", 0.7)),
            max_tokens=int(value.get("max_tokens", 512)),
            seed=int(value.get("seed", 1729)),
            timeout_seconds=int(value.get("timeout_seconds", 120)),
            system_prompt=str(value.get("system_prompt", "")),
            extra_request_fields=dict(value.get("extra_request_fields", {})),
        )
        config.validate()
        return config

    def to_mapping(self) -> dict[str, Any]:
        result = asdict(self)
        result["prompts"] = list(self.prompts)
        result["conditions"] = [asdict(item) for item in self.conditions]
        result["extra_request_fields"] = dict(self.extra_request_fields)
        return result


@dataclass(frozen=True)
class Completion:
    """Normalized completion returned by a chat adapter."""

    text: str
    finish_reason: str | None = None
    usage: Mapping[str, Any] = field(default_factory=dict)
    response_id: str | None = None


class ChatAdapter(Protocol):
    """Minimal interface required by the experiment runner."""

    def complete(
        self,
        messages: Sequence[Mapping[str, str]],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        seed: int,
        timeout_seconds: int,
        extra_request_fields: Mapping[str, Any],
    ) -> Completion:
        """Return one model completion."""


class OpenAICompatibleAdapter:
    """Small standard-library client for OpenAI-compatible chat endpoints."""

    def __init__(self, endpoint: str, api_key_env: str) -> None:
        self.endpoint = endpoint
        self.api_key_env = api_key_env

    def complete(
        self,
        messages: Sequence[Mapping[str, str]],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        seed: int,
        timeout_seconds: int,
        extra_request_fields: Mapping[str, Any],
    ) -> Completion:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"missing API key environment variable {self.api_key_env!r}"
            )

        payload: dict[str, Any] = {
            "model": model,
            "messages": list(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": seed,
        }
        payload.update(extra_request_fields)
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request, timeout=timeout_seconds
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"completion endpoint returned HTTP {exc.code}: {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"completion request failed: {exc.reason}") from exc

        try:
            choice = body["choices"][0]
            content = choice["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "completion response did not contain choices[0].message.content"
            ) from exc
        if not isinstance(content, str):
            raise RuntimeError("completion content must be a string")

        return Completion(
            text=content,
            finish_reason=choice.get("finish_reason"),
            usage=body.get("usage", {}),
            response_id=body.get("id"),
        )


class ReplayAdapter:
    """Deterministic adapter for tests and offline protocol demonstrations."""

    def __init__(self, outputs: Iterable[str]) -> None:
        self._outputs = iter(outputs)
        self.calls: list[list[dict[str, str]]] = []

    def complete(
        self,
        messages: Sequence[Mapping[str, str]],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        seed: int,
        timeout_seconds: int,
        extra_request_fields: Mapping[str, Any],
    ) -> Completion:
        del model, temperature, max_tokens, seed, timeout_seconds
        del extra_request_fields
        self.calls.append([dict(message) for message in messages])
        try:
            output = next(self._outputs)
        except StopIteration as exc:
            raise RuntimeError("ReplayAdapter has no outputs remaining") from exc
        return Completion(
            text=output,
            finish_reason="stop",
            usage={"replay": True},
            response_id=None,
        )


def _request_seed(base_seed: int, prompt_index: int, replicate: int, depth: int) -> int:
    return base_seed + prompt_index * 1_000_000 + replicate * 10_000 + depth


def _run_id(
    config: ExperimentConfig,
    condition: Condition,
    prompt: str,
    prompt_index: int,
    replicate: int,
) -> str:
    material = "\0".join(
        [
            config.model,
            condition.name,
            condition.input_policy,
            condition.history_policy,
            condition.observer_policy,
            str(prompt_index),
            str(replicate),
            str(config.seed),
            prompt,
        ]
    )
    return sha256_text(material)[:20]


def build_observation(
    *,
    policy: str,
    run_id: str,
    depth: int,
    previous_output: str | None,
) -> dict[str, Any] | None:
    """Build an accurate or matched-format sham state observation.

    The sham is deterministic, structurally identical, and guaranteed to differ
    from the accurate value.  The model-facing payload does not identify which
    policy generated it; that assignment remains in the trace.
    """

    if policy == "none":
        return None
    if policy not in {"accurate", "sham"}:
        raise ValueError(f"unsupported observer policy: {policy}")

    prior = previous_output or ""
    accurate = {
        "cycle_index": depth,
        "has_prior_output": previous_output is not None,
        "prior_output_sha256": sha256_text(prior) if previous_output else None,
        "prior_character_count": len(prior),
        "prior_word_count": len(prior.split()),
    }
    if policy == "accurate":
        return accurate

    digest = sha256_text(f"{run_id}\0{depth}\0sham")
    rng = random.Random(int(digest[:16], 16))
    delta_chars = rng.choice([-17, -11, -5, 7, 13, 19])
    delta_words = rng.choice([-7, -3, 2, 5, 9])
    return {
        "cycle_index": depth + rng.choice([-2, -1, 1, 2]),
        "has_prior_output": not accurate["has_prior_output"],
        "prior_output_sha256": digest,
        "prior_character_count": max(0, len(prior) + delta_chars),
        "prior_word_count": max(0, len(prior.split()) + delta_words),
    }


def inject_observation(input_text: str, observation: Mapping[str, Any]) -> str:
    """Append a machine-readable observer-state intervention to model input."""

    payload = json.dumps(
        observation,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (
        f"{input_text}\n\n"
        "[OBSERVER_STATE]\n"
        f"{payload}\n"
        "[/OBSERVER_STATE]"
    )


def _base_messages(system_prompt: str) -> list[dict[str, str]]:
    if not system_prompt:
        return []
    return [{"role": "system", "content": system_prompt}]


def verify_record_hash(record: Mapping[str, Any]) -> bool:
    """Verify the self-hash on a trace record."""

    expected = record.get("record_sha256")
    if not isinstance(expected, str):
        return False
    unhashed = dict(record)
    unhashed.pop("record_sha256", None)
    return canonical_hash(unhashed) == expected


def run_experiment(
    config: ExperimentConfig,
    adapter: ChatAdapter | None = None,
) -> tuple[Path, Path]:
    """Execute all configured runs and return trace and manifest paths."""

    config.validate()
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    trace_path = output_dir / "trace.jsonl"
    manifest_path = output_dir / "manifest.json"
    client = adapter or OpenAICompatibleAdapter(
        config.endpoint,
        config.api_key_env,
    )

    started_at = utc_now()
    record_count = 0
    run_count = 0
    with trace_path.open("w", encoding="utf-8") as trace_file:
        for prompt_index, prompt in enumerate(config.prompts):
            prompt_id = sha256_text(prompt)[:16]
            for condition in config.conditions:
                for replicate in range(config.replicates):
                    run_count += 1
                    run_id = _run_id(
                        config,
                        condition,
                        prompt,
                        prompt_index,
                        replicate,
                    )
                    previous_output: str | None = None
                    previous_record_hash: str | None = None
                    history = _base_messages(config.system_prompt)

                    for depth in range(config.depth):
                        input_text = (
                            prompt
                            if condition.input_policy == "seed"
                            else previous_output or prompt
                        )
                        observation = build_observation(
                            policy=condition.observer_policy,
                            run_id=run_id,
                            depth=depth,
                            previous_output=previous_output,
                        )
                        model_input = (
                            inject_observation(input_text, observation)
                            if observation is not None
                            else input_text
                        )
                        if condition.history_policy == "persistent":
                            history.append(
                                {"role": "user", "content": model_input}
                            )
                            messages = list(history)
                        else:
                            messages = _base_messages(config.system_prompt)
                            messages.append(
                                {"role": "user", "content": model_input}
                            )

                        request_seed = _request_seed(
                            config.seed,
                            prompt_index,
                            replicate,
                            depth,
                        )
                        completion = client.complete(
                            messages,
                            model=config.model,
                            temperature=config.temperature,
                            max_tokens=config.max_tokens,
                            seed=request_seed,
                            timeout_seconds=config.timeout_seconds,
                            extra_request_fields=config.extra_request_fields,
                        )
                        if condition.history_policy == "persistent":
                            history.append(
                                {
                                    "role": "assistant",
                                    "content": completion.text,
                                }
                            )

                        record: dict[str, Any] = {
                            "schema_version": SCHEMA_VERSION,
                            "run_id": run_id,
                            "timestamp_utc": utc_now(),
                            "model": config.model,
                            "condition": asdict(condition),
                            "prompt_id": prompt_id,
                            "seed_prompt": prompt,
                            "prompt_index": prompt_index,
                            "replicate": replicate,
                            "depth": depth,
                            "input_text": input_text,
                            "model_input": model_input,
                            "output_text": completion.text,
                            "input_sha256": sha256_text(input_text),
                            "model_input_sha256": sha256_text(model_input),
                            "output_sha256": sha256_text(completion.text),
                            "parent_output_sha256": (
                                sha256_text(previous_output)
                                if previous_output is not None
                                else None
                            ),
                            "parent_record_sha256": previous_record_hash,
                            "observer": (
                                {
                                    "assignment": condition.observer_policy,
                                    "payload": observation,
                                }
                                if observation is not None
                                else None
                            ),
                            "request": {
                                "temperature": config.temperature,
                                "max_tokens": config.max_tokens,
                                "seed": request_seed,
                                "history_message_count": len(messages),
                            },
                            "response": {
                                "finish_reason": completion.finish_reason,
                                "usage": dict(completion.usage),
                                "response_id": completion.response_id,
                            },
                        }
                        record["record_sha256"] = canonical_hash(record)
                        trace_file.write(
                            json.dumps(record, ensure_ascii=False, sort_keys=True)
                            + "\n"
                        )
                        trace_file.flush()
                        record_count += 1
                        previous_output = completion.text
                        previous_record_hash = record["record_sha256"]

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "status": "completed",
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "config": config.to_mapping(),
        "trace_file": trace_path.name,
        "trace_sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest(),
        "run_count": run_count,
        "record_count": record_count,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return trace_path, manifest_path


def load_config(path: str | Path) -> ExperimentConfig:
    """Load and validate a JSON experiment configuration."""

    config_path = Path(path)
    value = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("configuration root must be a JSON object")
    return ExperimentConfig.from_mapping(value, base_dir=config_path.parent)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run recursive output-to-input feedback experiments."
    )
    parser.add_argument("--config", required=True, help="Path to JSON config")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    trace_path, manifest_path = run_experiment(config)
    print(f"trace: {trace_path}")
    print(f"manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
