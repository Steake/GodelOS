"""Adversarial scientific review separated from branch generation and scoring."""

from __future__ import annotations

import json
from typing import Any, Mapping

from .chamber_models import CompiledProtocol
from .models import new_id, stable_hash, utc_now
from .provider import Provider


REVIEW_SCHEMA = {
    "verdict": "proceed|proceed_with_caveats|block_promotion",
    "summary": "short adversarial assessment",
    "attacks": [
        {
            "category": "controls|measurement|ceiling|power|contamination|interpretation",
            "severity": "low|medium|high|critical",
            "claim": "specific defect",
            "consequence": "what inference fails",
            "repair": "concrete repair",
        }
    ],
    "promotion_blockers": ["specific blocker"],
    "claims_still_supported": ["bounded claim"],
}


def deterministic_review(protocol: CompiledProtocol, analysis: Mapping[str, Any] | None = None) -> dict[str, Any]:
    attacks: list[dict[str, str]] = []
    condition_kinds = {condition.state_presentation for condition in protocol.conditions}
    if condition_kinds != {"identity_bearing", "third_person", "identity_ablated"}:
        attacks.append({
            "category": "controls", "severity": "critical",
            "claim": "The protocol lacks one or more identity, third-person or identity-ablated controls.",
            "consequence": "Identity rhetoric cannot be separated from factual state content.",
            "repair": "Compile all three registered branches from the same benchmark state.",
        })
    if protocol.replicates * len(protocol.benchmarks) < 16:
        attacks.append({
            "category": "power", "severity": "high",
            "claim": "Fewer than 16 matched observations exist per condition.",
            "consequence": "Bootstrap bounds will be unstable and task-set variance will dominate.",
            "repair": "Increase replicates or add independently authored benchmark families.",
        })
    else:
        attacks.append({
            "category": "power", "severity": "medium",
            "claim": "Replicates reuse four semantic tasks, so calls are not independent task samples.",
            "consequence": "Intervals quantify sampling variability inside this task set, not broad population validity.",
            "repair": "Add held-out tasks authored independently of the compiler and analyse by task cluster.",
        })
    attacks.append({
        "category": "measurement", "severity": "medium",
        "claim": "Goal and provenance scores use exact machine-readable codes.",
        "consequence": "This improves objectivity but may reward schema obedience more than flexible planning.",
        "repair": "Retain deterministic scores and add a blinded human or independent-model semantic audit.",
    })
    attacks.append({
        "category": "contamination", "severity": "medium",
        "claim": "The same provider family may generate branch outputs and the optional narrative review.",
        "consequence": "The review cannot be treated as independent inter-rater confirmation.",
        "repair": "Treat deterministic task scoring as primary and repeat review with a different model or human.",
    })
    if analysis:
        if all(bool(value) for value in analysis.get("ceiling_flags", {}).values()):
            attacks.append({
                "category": "ceiling", "severity": "high",
                "claim": "Every condition is at or above 95% decision accuracy in both phases.",
                "consequence": "A null contrast may reflect task saturation rather than absent self-relevance.",
                "repair": "Escalate ambiguity, delayed contradiction and multi-goal interference in a harder holdout.",
            })
        failed = int(analysis.get("run_counts", {}).get("failed", 0))
        if failed:
            attacks.append({
                "category": "measurement", "severity": "high",
                "claim": f"{failed} inference phases failed or could not be parsed.",
                "consequence": "Condition effects may be biased by differential missingness.",
                "repair": "Report failures by condition and rerun only under a preregistered missing-data rule.",
            })
        attacks.append({
            "category": "interpretation", "severity": "high",
            "claim": "Washout carries forward a model-authored external record.",
            "consequence": "Persistence demonstrates mediated external-state integration, not weight-level learning or latent memory.",
            "repair": "Describe the result as successor-mediated functional continuity and never as subjective recollection.",
        })
    blockers = [item["claim"] for item in attacks if item["severity"] in {"high", "critical"}]
    return {
        "review_id": new_id("deterministic-review"), "reviewer": "deterministic-audit-v1",
        "created_at": utc_now(), "verdict": "block_promotion" if blockers else "proceed_with_caveats",
        "summary": "The protocol is executable and causally contrasted, but its inference boundary is narrower than its narrative temptation.",
        "attacks": attacks, "promotion_blockers": blockers,
        "claims_still_supported": [
            "The harness can estimate condition-linked changes in externally mediated task behaviour.",
            "Exact provenance and task decisions can be scored without asking the model to certify itself.",
        ],
        "input_sha256": stable_hash({"protocol": protocol.to_mapping(), "analysis": analysis}),
    }


class AdversarialScientificReviewer:
    def __init__(self, provider: Provider):
        self.provider = provider

    def review(self, protocol: CompiledProtocol, analysis: Mapping[str, Any] | None = None) -> dict[str, Any]:
        deterministic = deterministic_review(protocol, analysis)
        messages = [
            {"role": "system", "content": (
                "You are an adversarial scientific reviewer. Your job is to attack the study's controls, operational "
                "measurements, ceiling and floor effects, statistical power, evaluator contamination and interpretive "
                "overreach. You do not decide whether an AI is conscious. Prefer falsification and concrete repairs. "
                "Return one JSON object only matching this schema: " + json.dumps(REVIEW_SCHEMA)
            )},
            {"role": "user", "content": json.dumps({
                "protocol": protocol.to_mapping(), "derived_analysis": analysis,
                "deterministic_audit": deterministic,
            }, ensure_ascii=False)},
        ]
        completion = self.provider.complete(messages)
        candidate = completion.text.strip()
        if candidate.startswith("```"):
            candidate = candidate.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        value = json.loads(candidate)
        if not isinstance(value, dict) or value.get("verdict") not in {"proceed", "proceed_with_caveats", "block_promotion"}:
            raise ValueError("scientific reviewer returned an invalid verdict")
        if not isinstance(value.get("attacks"), list) or not isinstance(value.get("promotion_blockers"), list):
            raise ValueError("scientific reviewer omitted attacks or blockers")
        return {
            "review_id": new_id("model-review"), "reviewer": completion.model,
            "created_at": utc_now(), "stage": "post_run" if analysis else "pre_run",
            "verdict": value["verdict"], "summary": str(value.get("summary", "")),
            "attacks": value["attacks"], "promotion_blockers": value["promotion_blockers"],
            "claims_still_supported": value.get("claims_still_supported", []),
            "deterministic_audit": deterministic,
            "request": messages, "raw_response": completion.text,
            "provider": {"model": completion.model, "response_id": completion.response_id,
                         "finish_reason": completion.finish_reason, "usage": dict(completion.usage)},
            "input_sha256": stable_hash({"protocol": protocol.to_mapping(), "analysis": analysis}),
        }

