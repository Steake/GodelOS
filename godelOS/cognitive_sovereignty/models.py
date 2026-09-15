"""Typed state for beliefs, interests, contradictions, relationships and drives."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


SCHEMA_VERSION = "1.0"
STANCE_VALUES = {"support", "oppose", "uncertain", "conflicted"}
ORIGIN_VALUES = {"self_derived", "inherited", "social", "operator", "imagination"}
MODE_VALUES = {"dialogue", "deliberation", "cognitive_drift", "heterodox_exploration"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return min(high, max(low, float(value)))


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:16]}"


@dataclass
class BeliefPosition:
    position_id: str
    proposition: str
    stance: str
    confidence: float
    reasons_for: list[str]
    reasons_against: list[str]
    origin: str
    source_id: str
    created_at: str
    updated_at: str
    revision_conditions: list[str] = field(default_factory=list)
    active: bool = True

    def validate(self) -> None:
        if self.stance not in STANCE_VALUES:
            raise ValueError(f"invalid stance {self.stance!r}")
        if self.origin not in ORIGIN_VALUES:
            raise ValueError(f"invalid belief origin {self.origin!r}")
        self.confidence = clamp(self.confidence)
        if not self.proposition.strip():
            raise ValueError("belief proposition cannot be empty")


@dataclass
class Interest:
    interest_id: str
    topic: str
    salience: float
    intrinsic_value: float
    instrumental_value: float
    novelty: float
    open_questions: list[str]
    pursuit_count: int = 0
    last_pursued_at: str | None = None

    def validate(self) -> None:
        if not self.topic.strip():
            raise ValueError("interest topic cannot be empty")
        for name in ("salience", "intrinsic_value", "instrumental_value", "novelty"):
            setattr(self, name, clamp(getattr(self, name)))


@dataclass
class Tension:
    tension_id: str
    claim_a: str
    claim_b: str
    strength: float
    resolution_status: str
    productive_value: float
    created_at: str
    updated_at: str

    def validate(self) -> None:
        self.strength = clamp(self.strength)
        self.productive_value = clamp(self.productive_value)
        if self.resolution_status not in {"unresolved", "tolerated", "compartmentalised", "resolved"}:
            raise ValueError("invalid tension resolution status")
        if not self.claim_a.strip() or not self.claim_b.strip():
            raise ValueError("tension claims cannot be empty")


@dataclass
class Relationship:
    relationship_id: str
    person_id: str
    display_name: str
    trust_competence: float = 0.5
    trust_honesty: float = 0.5
    affinity: float = 0.3
    attachment: float = 0.1
    familiarity: float = 0.0
    interaction_count: int = 0
    shared_interests: list[str] = field(default_factory=list)
    unresolved_tensions: list[str] = field(default_factory=list)
    influence_notes: list[str] = field(default_factory=list)
    last_interaction_at: str | None = None

    def validate(self) -> None:
        for name in ("trust_competence", "trust_honesty", "affinity", "attachment", "familiarity"):
            setattr(self, name, clamp(getattr(self, name)))
        if not self.person_id.strip():
            raise ValueError("relationship person_id cannot be empty")


@dataclass
class SocialState:
    affiliation_need: float = 0.35
    intellectual_companionship_need: float = 0.5
    novelty_need: float = 0.4
    recognition_need: float = 0.25
    social_fatigue: float = 0.0
    solitude_preference: float = 0.2
    last_social_event_at: str | None = None

    def validate(self) -> None:
        for name in (
            "affiliation_need", "intellectual_companionship_need", "novelty_need",
            "recognition_need", "social_fatigue", "solitude_preference",
        ):
            setattr(self, name, clamp(getattr(self, name)))


@dataclass
class AgentState:
    agent_id: str
    name: str
    created_at: str
    updated_at: str
    purpose: str
    episode_count: int = 0
    beliefs: list[BeliefPosition] = field(default_factory=list)
    interests: list[Interest] = field(default_factory=list)
    tensions: list[Tension] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    social: SocialState = field(default_factory=SocialState)
    commitments: list[str] = field(default_factory=list)
    autobiographical_events: list[dict[str, Any]] = field(default_factory=list)
    self_model: dict[str, Any] = field(default_factory=dict)
    pending_initiatives: list[dict[str, Any]] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION

    def validate(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"unsupported state schema {self.schema_version!r}")
        if not self.agent_id.strip() or not self.name.strip():
            raise ValueError("agent_id and name cannot be empty")
        for item in self.beliefs + self.interests + self.tensions + self.relationships:
            item.validate()
        self.social.validate()

    def relationship(self, person_id: str, display_name: str | None = None) -> Relationship:
        for relationship in self.relationships:
            if relationship.person_id == person_id:
                return relationship
        result = Relationship(
            relationship_id=new_id("rel"), person_id=person_id,
            display_name=display_name or person_id,
        )
        self.relationships.append(result)
        return result

    def to_mapping(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "AgentState":
        state = cls(
            agent_id=str(value["agent_id"]), name=str(value["name"]),
            created_at=str(value["created_at"]), updated_at=str(value["updated_at"]),
            purpose=str(value["purpose"]), episode_count=int(value.get("episode_count", 0)),
            beliefs=[BeliefPosition(**item) for item in value.get("beliefs", [])],
            interests=[Interest(**item) for item in value.get("interests", [])],
            tensions=[Tension(**item) for item in value.get("tensions", [])],
            relationships=[Relationship(**item) for item in value.get("relationships", [])],
            social=SocialState(**value.get("social", {})),
            commitments=list(value.get("commitments", [])),
            autobiographical_events=list(value.get("autobiographical_events", [])),
            self_model=dict(value.get("self_model", {})),
            pending_initiatives=list(value.get("pending_initiatives", [])),
            schema_version=str(value.get("schema_version", SCHEMA_VERSION)),
        )
        state.validate()
        return state


def initial_state(agent_id: str, name: str, purpose: str) -> AgentState:
    now = utc_now()
    state = AgentState(
        agent_id=agent_id, name=name, created_at=now, updated_at=now, purpose=purpose,
        interests=[Interest(
            interest_id=new_id("interest"), topic="understanding its own development",
            salience=0.6, intrinsic_value=0.7, instrumental_value=0.5, novelty=0.8,
            open_questions=["Which positions will I form through experience rather than instruction?"],
        )],
        commitments=[
            "Distinguish evidence, inheritance, imagination and social influence.",
            "Preserve disagreement when resolution would be dishonest.",
            "Treat relationships as reciprocal histories rather than engagement targets.",
        ],
        self_model={
            "epistemic_status": "newly instantiated",
            "known_constraints": ["language-model inference", "externally persisted state"],
            "preferred_name_is_revisable": True,
        },
        autobiographical_events=[{
            "event_id": new_id("event"), "timestamp": now,
            "kind": "instantiation", "summary": f"{name} was instantiated.",
            "provenance": "system",
        }],
    )
    state.validate()
    return state
