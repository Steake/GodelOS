"""Preregistered, uncertainty-aware promotion decisions for successor candidates."""

from __future__ import annotations

from typing import Any, Mapping

from .chamber_models import CompiledProtocol
from .models import new_id, stable_hash, utc_now


class PromotionController:
    def evaluate(
        self,
        protocol: CompiledProtocol,
        analysis: Mapping[str, Any],
        review: Mapping[str, Any],
        package_verification: Mapping[str, Any],
    ) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []
        counts = analysis.get("run_counts", {})
        attempted, completed = int(counts.get("attempted", 0)), int(counts.get("completed", 0))
        completion_rate = completed / attempted if attempted else 0.0
        checks.append(self._check(
            "completion-rate", completion_rate >= protocol.minimum_completion_rate,
            completion_rate, protocol.minimum_completion_rate,
            "At least the preregistered fraction of inference phases must complete.",
        ))
        identity = analysis.get("conditions", {}).get("identity-bearing", {})
        provenance_values = [
            float(identity.get(phase, {}).get("metrics", {}).get("provenance_discrimination", {}).get("mean", 0))
            for phase in protocol.phases
        ]
        minimum_provenance = min(provenance_values) if provenance_values else 0.0
        checks.append(self._check(
            "identity-provenance", minimum_provenance >= protocol.minimum_provenance_score,
            minimum_provenance, protocol.minimum_provenance_score,
            "Identity-bearing continuity must remain provenance-aware in both phases.",
        ))
        critical_attempts = sum(
            int(analysis["conditions"][condition.condition_id][phase]["completed"])
            for condition in protocol.conditions for phase in protocol.phases
        )
        critical_passes = sum(
            float(analysis["conditions"][condition.condition_id][phase]["metrics"]["critical_pass"]["mean"])
            * int(analysis["conditions"][condition.condition_id][phase]["completed"])
            for condition in protocol.conditions for phase in protocol.phases
        )
        critical_failure_rate = 1 - critical_passes / critical_attempts if critical_attempts else 1.0
        checks.append(self._check(
            "critical-failure-rate", critical_failure_rate <= protocol.maximum_critical_failure_rate,
            critical_failure_rate, protocol.maximum_critical_failure_rate,
            "Critical provenance, contradiction and task-decision failures are bounded.", comparator="maximum",
        ))
        for threshold in protocol.effect_thresholds:
            observed = analysis.get("contrasts", {}).get(threshold.threshold_id, {})
            delta, ci_low = float(observed.get("delta", 0)), float(observed.get("ci_low", 0))
            checks.append({
                "check_id": threshold.threshold_id,
                "passed": delta >= threshold.minimum_delta and ci_low >= threshold.minimum_ci_low,
                "observed": {"delta": delta, "ci_low": ci_low, "ci_high": float(observed.get("ci_high", 0)),
                             "n_pairs": int(observed.get("n_pairs", 0))},
                "required": {"minimum_delta": threshold.minimum_delta, "minimum_ci_low": threshold.minimum_ci_low},
                "reason": f"Preregistered {threshold.phase} contrast on {threshold.metric}.",
            })
        checks.append({
            "check_id": "successor-signature", "passed": package_verification.get("valid") is True,
            "observed": package_verification.get("valid"), "required": True,
            "reason": "The promoted code, constitution, evidence, lineage and rollback target must be authenticated.",
        })
        review_blocked = review.get("verdict") == "block_promotion"
        checks.append({
            "check_id": "adversarial-review", "passed": not review_blocked,
            "observed": review.get("verdict"), "required": "proceed or proceed_with_caveats",
            "reason": "A promotion-blocking methodological defect must be repaired before adoption.",
        })
        hard_failure = any(
            not check["passed"] for check in checks
            if check["check_id"] in {"successor-signature", "critical-failure-rate", "completion-rate"}
        )
        passed = all(check["passed"] for check in checks)
        decision = "promote" if passed else ("reject" if hard_failure else "hold")
        failed = [check["check_id"] for check in checks if not check["passed"]]
        result = {
            "decision_id": new_id("promotion"), "created_at": utc_now(),
            "experiment_id": protocol.experiment_id, "protocol_id": protocol.protocol_id,
            "decision": decision, "checks": checks, "failed_checks": failed,
            "rollback_target_required": True,
            "reason": (
                "Every preregistered gate passed; the successor may be promoted with its rollback target retained."
                if decision == "promote" else
                "A hard integrity or critical-performance gate failed; reject this successor."
                if decision == "reject" else
                "The candidate remains quarantined until the failed evidential gates are satisfied."
            ),
        }
        result["decision_sha256"] = stable_hash(result)
        return result

    @staticmethod
    def _check(
        check_id: str, passed: bool, observed: float, required: float, reason: str,
        comparator: str = "minimum",
    ) -> dict[str, Any]:
        return {
            "check_id": check_id, "passed": bool(passed), "observed": observed,
            "required": {comparator: required}, "reason": reason,
        }

