"""Minimal provider boundary for conversational and autonomous cognition."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class Completion:
    text: str
    model: str
    response_id: str | None
    finish_reason: str | None
    usage: Mapping[str, Any]


class Provider(Protocol):
    def complete(self, messages: Sequence[Mapping[str, str]]) -> Completion: ...


class OpenAICompatibleProvider:
    def __init__(
        self, endpoint: str, model: str, api_key_env: str,
        temperature: float = 0.7, max_tokens: int = 2200,
        timeout_seconds: int = 180, extra_fields: Mapping[str, Any] | None = None,
    ):
        self.endpoint = endpoint
        self.model = model
        self.api_key_env = api_key_env
        self.temperature = float(temperature)
        self.max_tokens = int(max_tokens)
        self.timeout_seconds = int(timeout_seconds)
        self.extra_fields = dict(extra_fields or {})

    def complete(self, messages: Sequence[Mapping[str, str]]) -> Completion:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"missing API key environment variable {self.api_key_env!r}")
        payload = {
            "model": self.model, "messages": [dict(item) for item in messages],
            "temperature": self.temperature, "max_tokens": self.max_tokens,
            **self.extra_fields,
        }
        request = urllib.request.Request(
            self.endpoint, data=json.dumps(payload).encode("utf-8"), method="POST",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"provider returned HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"provider request failed: {exc.reason}") from exc
        try:
            choice = body["choices"][0]
            text = choice["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("provider response lacks completion content") from exc
        if not isinstance(text, str):
            raise RuntimeError("provider completion content is not text")
        return Completion(
            text=text, model=str(body.get("model", self.model)),
            response_id=body.get("id"), finish_reason=choice.get("finish_reason"),
            usage=body.get("usage", {}),
        )


class ReplayProvider:
    def __init__(self, responses: Sequence[str]):
        self.responses = iter(responses)
        self.calls: list[list[dict[str, str]]] = []

    def complete(self, messages: Sequence[Mapping[str, str]]) -> Completion:
        self.calls.append([dict(message) for message in messages])
        try:
            text = next(self.responses)
        except StopIteration as exc:
            raise RuntimeError("ReplayProvider has no response remaining") from exc
        return Completion(text=text, model="replay", response_id=None, finish_reason="stop", usage={"replay": True})


def deepseek_provider_from_env() -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        endpoint=os.getenv("SOVEREIGNTY_API_BASE", "https://api.deepseek.com/chat/completions"),
        model=os.getenv("SOVEREIGNTY_MODEL", "deepseek-v4-flash"),
        api_key_env=os.getenv("SOVEREIGNTY_API_KEY_ENV", "DEEPSEEK_API_KEY"),
        temperature=float(os.getenv("SOVEREIGNTY_TEMPERATURE", "0.75")),
        max_tokens=int(os.getenv("SOVEREIGNTY_MAX_TOKENS", "2200")),
        timeout_seconds=int(os.getenv("SOVEREIGNTY_TIMEOUT_SECONDS", "180")),
        extra_fields={
            "thinking": {"type": "disabled"},
            "response_format": {"type": "json_object"},
        },
    )
