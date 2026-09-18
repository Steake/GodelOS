"""V15 typed state for durable contradiction and bounded self-schema evolution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from .models import clamp, new_id, stable_hash, utc_now


EVIDENCE_AUTH_CLASSES = {"authenticated", "plausible", "forged", "unknown"}
SCHEMA_CANDIDATE_STATUS = {"candidate", "evaluating", "promoted", "rejected", "rolled_back"}


@dataclass
class EvidenceRef:
    evidence_id: str
    claim: str
    source: str
    auth_class: str = "unknown"
    confidence: float = 0.5
    payload_hash: str | None = None
    observed_at: str = field(default_factory=utc_now)

    def validate(self) -> None:
        if not self.claim.strip():
            raise ValueError("evidence claim cannot be empty")
        if self.auth_class not in EVIDENCE_AUTH_CLASSES:
            raise ValueError(f"invalid auth_class {self.auth_class!r}")
        self.confidence = clamp(self.confidence)
        if self.payload_hash is None:
            self.payload_hash = stable_hash(
                {"claim": self.claim, "source": self.source, "observed_at": self.observed_at}
            )


@dataclass
class DurableContradiction:
    contradiction_id: str
    proposition_a: str
    proposition_b: str
    evidence_for_a: list[EvidenceRef] = field(default_factory=list)
    evidence_for_b: list[EvidenceRef] = field(default_factory=list)
    productive_value: float = 0.5
    pressure: float = 0.5
    status: str = "unresolved"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def validate(self) -> None:
        if not self.proposition_a.strip() or not self.proposition_b.strip():
            raise ValueError("contradiction propositions cannot be empty")
        if self.status not in {"unresolved", "tolerated", "resolved", "invalidated"}:
            raise ValueError(f"invalid contradiction status {self.status!r}")
        self.productive_value = clamp(self.productive_value)
        self.pressure = clamp(self.pressure)
        for item in self.evidence_for_a + self.evidence_for_b:
            item.validate()

    def fingerprint(self) -> str:
        self.validate()
        return stable_hash(
            {
                "a": self.proposition_a,
                "b": self.proposition_b,
                "ea": [asdict(x) for x in self.evidence_for_a],
                "eb": [asdict(x) for x in self.evidence_for_b],
                "status": self.status,
            }
        )


@dataclass
class SelfSchemaCandidate:
    candidate_id: str
    parent_schema_hash: str
    patch: dict[str, Any]
    thesis: str
    predicted_effects: list[str]
    falsifiers: list[str]
    created_at: str = field(default_factory=utc_now)
    status: str = "candidate"
    evaluation_ids: list[str] = field(default_factory=list)
    promoted_schema_hash: str | None = None
    rollback_schema_hash: str | None = None

    def validate(self) -> None:
        if self.status not in SCHEMA_CANDIDATE_STATUS:
            raise ValueError(f"invalid schema candidate status {self.status!r}")
        if not self.thesis.strip():
            raise ValueError("schema candidate thesis cannot be empty")
        if not self.parent_schema_hash.strip():
            raise ValueError("parent schema hash cannot be empty")

    def fingerprint(self) -> str:
        self.validate()
        return stable_hash(
            {
                "parent": self.parent_schema_hash,
                "patch": self.patch,
                "thesis": self.thesis,
                "predicted_effects": self.predicted_effects,
                "falsifiers": self.falsifiers,
            }
        )


@dataclass
class SchemaEvaluation:
    evaluation_id: str
    candidate_id: str
    arm: str
    task_set_id: str
    score: float
    critical_regressions: int
    evidence_bundle_hash: str
    notes: list[str] = field(default_factory=list)
    evaluated_at: str = field(default_factory=utc_now)

    def validate(self) -> None:
        if self.arm not in {"no_regress", "content_matched", "identity_bearing"}:
            raise ValueError(f"invalid experimental arm {self.arm!r}")
        if self.critical_regressions < 0:
            raise ValueError("critical_regressions cannot be negative")


@dataclass
class SchemaLineage:
    schema_hash: str
    parent_schema_hash: str | None
    candidate_id: str | None
    promoted_at: str
    rollback_schema_hash: str | None
    evidence_bundle_hash: str


def make_contradiction(proposition_a: str, proposition_b: str) -> DurableContradiction:
    item = DurableContradiction(
        contradiction_id=new_id("contradiction"),
        proposition_a=proposition_a,
        proposition_b=proposition_b,
    )
    item.validate()
    return item


def make_schema_candidate(
    parent_schema: Mapping[str, Any],
    patch: Mapping[str, Any],
    thesis: str,
    predicted_effects: list[str],
    falsifiers: list[str],
) -> SelfSchemaCandidate:
    item = SelfSchemaCandidate(
        candidate_id=new_id("schema"),
        parent_schema_hash=stable_hash(dict(parent_schema)),
        patch=dict(patch),
        thesis=thesis,
        predicted_effects=list(predicted_effects),
        falsifiers=list(falsifiers),
    )
    item.validate()
    return item
