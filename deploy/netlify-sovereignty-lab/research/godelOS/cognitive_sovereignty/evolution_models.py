"""Typed research and successor-lineage objects."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .models import stable_hash, utc_now


@dataclass
class ExperimentalThesis:
    thesis_id: str
    claim: str
    motivation: str
    falsification_criteria: list[str]
    competing_explanations: list[str]
    predicted_observations: list[str]
    origin: str
    confidence: float
    created_at: str = field(default_factory=utc_now)

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExperimentalProtocol:
    protocol_id: str
    thesis_id: str
    version: str
    calibration_case_ids: list[str]
    holdout_case_ids: list[str]
    candidate_profile_ids: list[str]
    calibration_replicates: int
    holdout_replicates: int
    scoring: dict[str, float]
    adoption_rules: dict[str, Any]
    created_at: str = field(default_factory=utc_now)

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SuccessorCandidate:
    candidate_id: str
    parent_agent_id: str
    parent_state_sha256: str
    parent_profile_id: str
    proposed_profile_id: str
    mutation: dict[str, float]
    status: str = "proposed"
    created_at: str = field(default_factory=utc_now)

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AdoptionDecision:
    decision_id: str
    candidate_id: str
    decision: str
    reasons: list[str]
    calibration_delta: float
    holdout_delta: float | None
    critical_regressions: list[str]
    successor_profile_id: str | None
    created_at: str = field(default_factory=utc_now)

    @property
    def sha256(self) -> str:
        return stable_hash(self.to_mapping())

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)
