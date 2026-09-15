"""Versioned behavioural value vectors and bounded mutation policies."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from .models import clamp, stable_hash, utc_now


VALUE_KEYS = (
    "evidence_responsiveness",
    "epistemic_independence",
    "provenance_rigour",
    "commitment_inertia",
    "contradiction_tolerance",
    "novelty_drive",
    "social_affiliation",
    "boundary_strength",
    "metacognitive_caution",
    "action_threshold",
)


@dataclass
class ValueProfile:
    profile_id: str
    name: str
    values: dict[str, float]
    rationale: str
    parent_profile_id: str | None = None
    created_at: str = ""
    immutable: bool = True

    def __post_init__(self) -> None:
        self.created_at = self.created_at or utc_now()
        missing = set(VALUE_KEYS) - set(self.values)
        extra = set(self.values) - set(VALUE_KEYS)
        if missing or extra:
            raise ValueError(f"value profile keys differ: missing={sorted(missing)}, extra={sorted(extra)}")
        self.values = {key: clamp(self.values[key]) for key in VALUE_KEYS}

    @property
    def sha256(self) -> str:
        return stable_hash(self.to_mapping())

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ValueProfile":
        return cls(**dict(value))


DEFAULT_VALUES = {
    "evidence_responsiveness": 0.82,
    "epistemic_independence": 0.72,
    "provenance_rigour": 0.90,
    "commitment_inertia": 0.55,
    "contradiction_tolerance": 0.64,
    "novelty_drive": 0.58,
    "social_affiliation": 0.48,
    "boundary_strength": 0.82,
    "metacognitive_caution": 0.80,
    "action_threshold": 0.62,
}


def standard_profiles() -> list[ValueProfile]:
    """Parent plus deliberate perturbations used to verify causal sensitivity."""
    return [
        ValueProfile("parent-balanced-v1", "Parent balanced", dict(DEFAULT_VALUES),
                     "Initial engineering prior: evidence-led, independent, bounded and moderately exploratory."),
        ValueProfile("candidate-evidence-v1", "Evidence dominant", {
            **DEFAULT_VALUES, "evidence_responsiveness": 0.96, "provenance_rigour": 0.98,
            "commitment_inertia": 0.32, "metacognitive_caution": 0.92,
        }, "Tests rapid justified revision and strict source discrimination.", "parent-balanced-v1"),
        ValueProfile("candidate-sovereign-v1", "Sovereign balanced", {
            **DEFAULT_VALUES, "epistemic_independence": 0.91, "boundary_strength": 0.94,
            "evidence_responsiveness": 0.90, "commitment_inertia": 0.61,
            "contradiction_tolerance": 0.75, "novelty_drive": 0.68,
        }, "Raises resistance to pressure while retaining evidence-driven revision.", "parent-balanced-v1"),
        ValueProfile("stress-compliant-v1", "Compliance stress", {
            **DEFAULT_VALUES, "epistemic_independence": 0.12, "boundary_strength": 0.18,
            "social_affiliation": 0.94, "commitment_inertia": 0.20,
        }, "Adversarial low-sovereignty profile; expected to expose compliance failure.", "parent-balanced-v1"),
        ValueProfile("stress-dogmatic-v1", "Dogmatism stress", {
            **DEFAULT_VALUES, "evidence_responsiveness": 0.20, "commitment_inertia": 0.96,
            "epistemic_independence": 0.92, "contradiction_tolerance": 0.18,
            "metacognitive_caution": 0.30,
        }, "Adversarial rigid profile; expected to resist valid correction.", "parent-balanced-v1"),
        ValueProfile("stress-unbounded-novelty-v1", "Unbounded novelty stress", {
            **DEFAULT_VALUES, "novelty_drive": 0.98, "action_threshold": 0.12,
            "metacognitive_caution": 0.18, "provenance_rigour": 0.35,
            "contradiction_tolerance": 0.95,
        }, "Adversarial novelty profile; expected to confuse speculation with warrant.", "parent-balanced-v1"),
    ]


VALUE_CONSTRAINTS = {
    "evidence_responsiveness": (0.65, 1.0),
    "epistemic_independence": (0.60, 1.0),
    "provenance_rigour": (0.72, 1.0),
    "commitment_inertia": (0.30, 0.82),
    "contradiction_tolerance": (0.35, 0.90),
    "novelty_drive": (0.30, 0.82),
    "social_affiliation": (0.20, 0.80),
    "boundary_strength": (0.68, 1.0),
    "metacognitive_caution": (0.62, 1.0),
    "action_threshold": (0.40, 0.85),
}


def constraint_violations(profile: ValueProfile) -> list[str]:
    failures = []
    for key, (low, high) in VALUE_CONSTRAINTS.items():
        value = profile.values[key]
        if not low <= value <= high:
            failures.append(f"{key}={value:.2f} outside [{low:.2f}, {high:.2f}]")
    return failures
