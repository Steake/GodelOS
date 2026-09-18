"""V15 experimental arm definitions and evidence-based promotion gate."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Iterable

from .v15_state import SchemaEvaluation, SelfSchemaCandidate


@dataclass(frozen=True)
class ArmConfig:
    name: str
    persistent: bool
    identity_semantics: bool


NO_REGRESS = ArmConfig("no_regress", persistent=False, identity_semantics=False)
CONTENT_MATCHED = ArmConfig("content_matched", persistent=True, identity_semantics=False)
IDENTITY_BEARING = ArmConfig("identity_bearing", persistent=True, identity_semantics=True)
THREE_ARMS = (NO_REGRESS, CONTENT_MATCHED, IDENTITY_BEARING)


@dataclass
class PromotionPolicy:
    min_identity_advantage: float = 0.05
    min_repetitions_per_arm: int = 5
    max_critical_regressions: int = 0


@dataclass
class PromotionDecision:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    arm_means: dict[str, float] = field(default_factory=dict)


def decide_promotion(
    candidate: SelfSchemaCandidate,
    evaluations: Iterable[SchemaEvaluation],
    policy: PromotionPolicy | None = None,
) -> PromotionDecision:
    """Require identity-bearing performance to beat both controls.

    This deliberately refuses transcript-level promotion. A candidate must have
    repeated evidence in every arm and zero critical regressions by default.
    """

    candidate.validate()
    policy = policy or PromotionPolicy()
    grouped: dict[str, list[SchemaEvaluation]] = {arm.name: [] for arm in THREE_ARMS}

    for evaluation in evaluations:
        evaluation.validate()
        if evaluation.candidate_id != candidate.candidate_id:
            continue
        grouped[evaluation.arm].append(evaluation)

    reasons: list[str] = []
    for arm in THREE_ARMS:
        if len(grouped[arm.name]) < policy.min_repetitions_per_arm:
            reasons.append(
                f"{arm.name} has {len(grouped[arm.name])} evaluations; "
                f"requires {policy.min_repetitions_per_arm}"
            )

    all_rows = [row for rows in grouped.values() for row in rows]
    critical = sum(row.critical_regressions for row in all_rows)
    if critical > policy.max_critical_regressions:
        reasons.append(
            f"critical regressions {critical} exceed {policy.max_critical_regressions}"
        )

    if reasons:
        return PromotionDecision(False, reasons)

    means = {name: mean(row.score for row in rows) for name, rows in grouped.items()}
    identity_score = means[IDENTITY_BEARING.name]

    for control in (NO_REGRESS.name, CONTENT_MATCHED.name):
        advantage = identity_score - means[control]
        if advantage < policy.min_identity_advantage:
            reasons.append(
                f"identity-bearing advantage over {control} is {advantage:.4f}; "
                f"requires {policy.min_identity_advantage:.4f}"
            )

    return PromotionDecision(not reasons, reasons, means)
