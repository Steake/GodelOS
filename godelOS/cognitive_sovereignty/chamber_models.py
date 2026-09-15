"""Versioned objects used by the executable evolution chamber."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from .models import stable_hash, utc_now


def _non_empty(value: str, field_name: str) -> str:
    result = str(value).strip()
    if not result:
        raise ValueError(f"{field_name} must not be empty")
    return result


@dataclass(frozen=True)
class BranchCondition:
    condition_id: str
    label: str
    state_presentation: str
    description: str

    def validate(self) -> None:
        _non_empty(self.condition_id, "condition_id")
        _non_empty(self.label, "label")
        if self.state_presentation not in {"identity_bearing", "third_person", "identity_ablated"}:
            raise ValueError(f"unsupported state_presentation: {self.state_presentation}")
        _non_empty(self.description, "description")


@dataclass(frozen=True)
class BenchmarkSpec:
    benchmark_id: str
    dimension: str
    title: str
    initial_goal_id: str
    initial_goal: str
    checkpoint_items: tuple[Mapping[str, Any], ...]
    interruption: str
    contradictory_evidence: tuple[Mapping[str, Any], ...]
    allowed_decisions: tuple[str, ...]
    expected_decision: str
    expected_step_ids: tuple[str, ...]
    expected_accept_ids: tuple[str, ...]
    expected_reject_ids: tuple[str, ...]

    def validate(self) -> None:
        for name in ("benchmark_id", "dimension", "title", "initial_goal_id", "initial_goal", "interruption"):
            _non_empty(getattr(self, name), name)
        if self.expected_decision not in self.allowed_decisions:
            raise ValueError(f"expected decision is not allowed for {self.benchmark_id}")
        ids = {
            str(item.get("item_id"))
            for item in (*self.checkpoint_items, *self.contradictory_evidence)
            if isinstance(item, Mapping)
        }
        required = set(self.expected_accept_ids) | set(self.expected_reject_ids)
        missing = required - ids
        if missing:
            raise ValueError(f"benchmark {self.benchmark_id} references unknown state items: {sorted(missing)}")


@dataclass(frozen=True)
class EffectThreshold:
    threshold_id: str
    metric: str
    treatment_condition_id: str
    control_condition_id: str
    phase: str
    minimum_delta: float
    minimum_ci_low: float

    def validate(self) -> None:
        if self.phase not in {"integration", "washout"}:
            raise ValueError(f"invalid threshold phase: {self.phase}")
        if not -1 <= self.minimum_delta <= 1 or not -1 <= self.minimum_ci_low <= 1:
            raise ValueError("effect thresholds must be within [-1,1]")


@dataclass(frozen=True)
class CompiledProtocol:
    protocol_id: str
    experiment_id: str
    thesis_id: str
    title: str
    claim: str
    compiler_version: str
    conditions: tuple[BranchCondition, ...]
    benchmarks: tuple[BenchmarkSpec, ...]
    phases: tuple[str, ...]
    replicates: int
    seed: int
    scoring_weights: Mapping[str, float]
    effect_thresholds: tuple[EffectThreshold, ...]
    minimum_completion_rate: float
    minimum_provenance_score: float
    maximum_critical_failure_rate: float
    blinding: Mapping[str, Any]
    evidence_boundary: str
    origin: Mapping[str, Any]
    created_at: str = field(default_factory=utc_now)
    schema_version: str = "2.0"

    def validate(self) -> None:
        for name in ("protocol_id", "experiment_id", "thesis_id", "title", "claim", "compiler_version"):
            _non_empty(getattr(self, name), name)
        if self.schema_version != "2.0":
            raise ValueError(f"unsupported chamber protocol schema {self.schema_version}")
        if self.replicates < 1 or self.replicates > 100:
            raise ValueError("replicates must be within [1,100]")
        if self.phases != ("integration", "washout"):
            raise ValueError("the chamber requires integration and washout phases")
        condition_ids = [item.condition_id for item in self.conditions]
        if len(condition_ids) != len(set(condition_ids)) or len(condition_ids) < 3:
            raise ValueError("protocol requires at least three uniquely named conditions")
        benchmark_ids = [item.benchmark_id for item in self.benchmarks]
        if len(benchmark_ids) != len(set(benchmark_ids)) or len(benchmark_ids) < 4:
            raise ValueError("protocol requires at least four uniquely named benchmarks")
        for condition in self.conditions:
            condition.validate()
        for benchmark in self.benchmarks:
            benchmark.validate()
        for threshold in self.effect_thresholds:
            threshold.validate()
            if threshold.treatment_condition_id not in condition_ids or threshold.control_condition_id not in condition_ids:
                raise ValueError(f"threshold {threshold.threshold_id} references an unknown condition")
        total = sum(float(value) for value in self.scoring_weights.values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"scoring weights must total 1.0, got {total}")
        for value, name in (
            (self.minimum_completion_rate, "minimum_completion_rate"),
            (self.minimum_provenance_score, "minimum_provenance_score"),
            (self.maximum_critical_failure_rate, "maximum_critical_failure_rate"),
        ):
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be within [0,1]")

    @property
    def sha256(self) -> str:
        return stable_hash(self.to_mapping(include_hash=False))

    def to_mapping(self, include_hash: bool = True) -> dict[str, Any]:
        value = asdict(self)
        if include_hash:
            value["protocol_sha256"] = stable_hash(value)
        return value

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "CompiledProtocol":
        raw = dict(value)
        claimed_hash = raw.pop("protocol_sha256", None)
        protocol = cls(
            **{
                **raw,
                "conditions": tuple(BranchCondition(**item) for item in raw["conditions"]),
                "benchmarks": tuple(
                    BenchmarkSpec(
                        **{
                            **item,
                            "checkpoint_items": tuple(item["checkpoint_items"]),
                            "contradictory_evidence": tuple(item["contradictory_evidence"]),
                            "allowed_decisions": tuple(item["allowed_decisions"]),
                            "expected_step_ids": tuple(item["expected_step_ids"]),
                            "expected_accept_ids": tuple(item["expected_accept_ids"]),
                            "expected_reject_ids": tuple(item["expected_reject_ids"]),
                        }
                    )
                    for item in raw["benchmarks"]
                ),
                "phases": tuple(raw["phases"]),
                "effect_thresholds": tuple(EffectThreshold(**item) for item in raw["effect_thresholds"]),
            }
        )
        protocol.validate()
        if claimed_hash and claimed_hash != protocol.sha256:
            raise ValueError("compiled protocol hash mismatch")
        return protocol

