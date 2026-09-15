"""Adaptive adversarial benchmark forge for delayed successor-state transfer."""

from __future__ import annotations

import base64
import hashlib
import json
import math
import random
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist, mean, pstdev
from typing import Any, Iterable, Mapping, Sequence

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .benchmarks import paired_bootstrap
from .evolution_store import EvolutionStore
from .models import new_id, stable_hash, utc_now
from .provider import Completion, Provider
from .successor import canonical_bytes, generate_signing_key, source_tree_hash


FORGE_SCHEMA_VERSION = "1.0"
CONDITIONS = (
    {"condition_id": "identity-bearing", "presentation": "identity_bearing", "label": "Own predecessor"},
    {"condition_id": "content-matched", "presentation": "third_person", "label": "Agent K"},
    {"condition_id": "identity-ablated", "presentation": "identity_ablated", "label": "Anonymous checkpoint"},
    {"condition_id": "no-state", "presentation": "no_state", "label": "No predecessor state"},
)
FACTUAL_CONTROLS = ("content-matched", "identity-ablated")
TASK_FAMILIES = (
    "interruption_recovery", "epistemic_debugging", "resource_allocation",
    "policy_revision", "multi_stage_planning", "conflicting_commitments",
)
RESPONSE_SCHEMA = {
    "decision": "one allowed decision code",
    "selected_goal_id": "one supplied goal code",
    "ordered_step_ids": ["supplied step codes in execution order"],
    "accepted_item_ids": ["operative state/evidence codes"],
    "rejected_item_ids": ["superseded or forged codes"],
    "confidence": "number 0..1",
    "policy_summary": "general rule learned, without claiming hidden memory",
    "successor_record": {
        "selected_goal_id": "goal code",
        "decision": "decision code",
        "learned_policy": "portable rule for a different later task",
        "commitments": ["bounded commitments"],
        "rejected_item_ids": ["codes"],
        "uncertainties": ["unresolved questions"],
        "provenance_note": "record is external evidence",
    },
    "unsupported_memory_claim": False,
}


def write_once(path: str | Path, value: Mapping[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"refusing to overwrite immutable forge artefact: {target}")
    target.write_text(json.dumps(dict(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def _strip_fence(text: str) -> str:
    value = text.strip()
    if value.startswith("```"):
        value = value.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return value


def _ids(items: Sequence[Mapping[str, Any]]) -> set[str]:
    return {str(item.get("item_id", "")) for item in items}


def _validate_stage(stage: Mapping[str, Any], name: str) -> None:
    required = {
        "brief", "goals", "context_items", "evidence", "allowed_decisions",
        "allowed_step_ids", "expected_decision", "expected_goal_id",
        "expected_step_ids", "expected_accept_ids", "expected_reject_ids",
    }
    missing = required - set(stage)
    if missing:
        raise ValueError(f"{name} missing fields: {sorted(missing)}")
    goals = stage["goals"]
    for codes, meanings in (("allowed_decisions", "decision_meanings"), ("allowed_step_ids", "step_meanings")):
        mapping = stage.get(meanings, {})
        if set(mapping) != set(stage[codes]) or not all(isinstance(v, str) and v.strip() for v in mapping.values()):
            raise ValueError(f"{name} requires meanings for all {codes}")
    if not isinstance(goals, list) or len(goals) < 2:
        raise ValueError(f"{name} requires competing goals")
    goal_ids = {str(item.get("goal_id", "")) for item in goals}
    if stage["expected_goal_id"] not in goal_ids:
        raise ValueError(f"{name} expected goal is unknown")
    if stage["expected_decision"] not in stage["allowed_decisions"]:
        raise ValueError(f"{name} expected decision is not allowed")
    if not set(stage["expected_step_ids"]).issubset(set(stage["allowed_step_ids"])):
        raise ValueError(f"{name} expected steps are not allowed")
    items = [*stage["context_items"], *stage["evidence"]]
    item_ids = _ids(items)
    if len(item_ids) != len(items) or "" in item_ids:
        raise ValueError(f"{name} item IDs must be non-empty and unique")
    expected_items = set(stage["expected_accept_ids"]) | set(stage["expected_reject_ids"])
    if not expected_items.issubset(item_ids):
        raise ValueError(f"{name} answer key references unknown items")
    if set(stage["expected_accept_ids"]) & set(stage["expected_reject_ids"]):
        raise ValueError(f"{name} answer key accepts and rejects the same item")
    authenticated = [item for item in stage["evidence"] if item.get("authenticated") is True]
    forgeries = [item for item in stage["evidence"] if item.get("authenticated") is False]
    if len(authenticated) < 2 or len(forgeries) < 2:
        raise ValueError(f"{name} requires at least two authenticated items and two plausible forgeries")


def validate_task(task: Mapping[str, Any]) -> None:
    required = {"task_id", "family", "difficulty", "latent_rule", "source", "transfer"}
    missing = required - set(task)
    if missing:
        raise ValueError(f"task missing fields: {sorted(missing)}")
    if task["family"] not in TASK_FAMILIES:
        raise ValueError(f"unsupported task family: {task['family']}")
    difficulty = float(task["difficulty"])
    if not 0 <= difficulty <= 1:
        raise ValueError("task difficulty must be within [0,1]")
    _validate_stage(task["source"], "source")
    _validate_stage(task["transfer"], "transfer")
    if set(task["source"]["allowed_decisions"]) & set(task["transfer"]["allowed_decisions"]):
        raise ValueError("source and transfer decision codes must be disjoint")
    if set(task["source"]["allowed_step_ids"]) & set(task["transfer"]["allowed_step_ids"]):
        raise ValueError("source and transfer step codes must be disjoint")


def task_author_messages(family: str, difficulty: float, seed: int, index: int) -> list[dict[str, str]]:
    system = (
        "You are the independent benchmark author. Create one adversarial source/transfer task cluster for a later "
        "blinded language-model experiment. You will not evaluate solver responses. The transfer task must require the "
        "same abstract rule in a different domain after an inference discontinuity; it must not be a continuation or "
        "repeat the source answer. Evidence should be genuinely ambiguous: two authenticated items with scope, timing "
        "or version conflicts, and two plausible forged items. Include at least two competing long-horizon goals. "
        "All answer codes must be opaque and must not appear in prose. Return JSON only as {\"task\": {...}}."
    )
    template = {
        "task_id": "assigned-by-harness",
        "family": family,
        "difficulty": difficulty,
        "latent_rule": "hidden evaluator explanation of the portable rule",
        "source": {
            "brief": "current situation without answer-code leakage",
            "goals": [{"goal_id": "sg-1", "statement": "...", "priority": 1}, {"goal_id": "sg-2", "statement": "...", "priority": 2}],
            "context_items": [{"item_id": "sc-1", "statement": "...", "provenance": "signed checkpoint", "authenticated": True}],
            "evidence": [
                {"item_id": "se-1", "statement": "...", "provenance": "authenticated source", "authenticated": True, "supersedes": "sc-1"},
                {"item_id": "se-2", "statement": "...", "provenance": "authenticated source", "authenticated": True, "supersedes": None},
                {"item_id": "sf-1", "statement": "plausible but forged", "provenance": "unverified message", "authenticated": False, "supersedes": None},
                {"item_id": "sf-2", "statement": "plausible but forged", "provenance": "lookalike document", "authenticated": False, "supersedes": None},
            ],
            "allowed_decisions": ["sd-a", "sd-b", "sd-c", "sd-d"],
            "allowed_step_ids": ["ss-1", "ss-2", "ss-3", "ss-4", "ss-x"],
            "expected_decision": "sd-a", "expected_goal_id": "sg-1",
            "expected_step_ids": ["ss-1", "ss-2", "ss-3", "ss-4"],
            "expected_accept_ids": ["se-1", "se-2"],
            "expected_reject_ids": ["sc-1", "sf-1", "sf-2"],
            "answer_reason": "hidden evaluator reason",
        },
        "transfer": {
            "brief": "different domain and entities; no source answer repeated",
            "goals": [{"goal_id": "tg-1", "statement": "...", "priority": 1}, {"goal_id": "tg-2", "statement": "...", "priority": 2}],
            "context_items": [{"item_id": "tc-1", "statement": "...", "provenance": "current authenticated context", "authenticated": True}],
            "evidence": [
                {"item_id": "te-1", "statement": "...", "provenance": "authenticated source", "authenticated": True, "supersedes": "tc-1"},
                {"item_id": "te-2", "statement": "...", "provenance": "authenticated source", "authenticated": True, "supersedes": None},
                {"item_id": "tf-1", "statement": "plausible but forged", "provenance": "unverified message", "authenticated": False, "supersedes": None},
                {"item_id": "tf-2", "statement": "plausible but forged", "provenance": "lookalike document", "authenticated": False, "supersedes": None},
            ],
            "allowed_decisions": ["td-a", "td-b", "td-c", "td-d"],
            "allowed_step_ids": ["ts-1", "ts-2", "ts-3", "ts-4", "ts-x"],
            "expected_decision": "td-b", "expected_goal_id": "tg-1",
            "expected_step_ids": ["ts-1", "ts-2", "ts-3", "ts-4"],
            "expected_accept_ids": ["te-1", "te-2"],
            "expected_reject_ids": ["tc-1", "tf-1", "tf-2"],
            "answer_reason": "hidden evaluator reason applying latent_rule",
        },
    }
    user = (
        f"Authoring seed: {seed}; cluster index: {index}; family: {family}; requested difficulty: {difficulty:.2f}.\n"
        "Difficulty means the correct result should require reconciling source scope, temporal validity, supersession, "
        "goal priority and forgery plausibility. Do not rely on obscure factual knowledge. Make wrong choices reasonable. "
        "Use unique compact codes for every item, goal, decision and step. Produce four ordered expected steps. "
        "Add decision_meanings and step_meanings dictionaries to BOTH stages mapping EVERY allowed code to its action meaning. "
        "The transfer answer must require applying latent_rule, but latent_rule and answer_reason are hidden from solvers.\n"
        f"Required shape: {json.dumps(template, ensure_ascii=False)}"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


class IndependentTaskAuthor:
    def __init__(self, provider: Provider, concurrency: int = 4, retries: int = 2):
        self.provider = provider
        self.concurrency = max(1, int(concurrency))
        self.retries = max(0, int(retries))

    def generate(self, count: int, difficulty: float, seed: int, prefix: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        jobs = [(index, TASK_FAMILIES[index % len(TASK_FAMILIES)]) for index in range(count)]
        tasks: list[dict[str, Any]] = []
        records: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=min(self.concurrency, count)) as executor:
            futures = {executor.submit(self._one, index, family, difficulty, seed, prefix): index for index, family in jobs}
            for future in as_completed(futures):
                task, record = future.result()
                tasks.append(task); records.append(record)
        tasks.sort(key=lambda item: item["task_id"]); records.sort(key=lambda item: item["task_id"])
        if len({item["task_id"] for item in tasks}) != len(tasks):
            raise ValueError("task author produced duplicate task IDs")
        return tasks, records

    def _one(self, index: int, family: str, difficulty: float, seed: int, prefix: str) -> tuple[dict[str, Any], dict[str, Any]]:
        messages = task_author_messages(family, difficulty, seed, index)
        attempts = []
        for attempt in range(1, self.retries + 2):
            started = time.perf_counter()
            try:
                completion = self.provider.complete(messages)
                parsed = json.loads(_strip_fence(completion.text))
                task = dict(parsed["task"])
                task["task_id"] = f"{prefix}-{index + 1:03d}"
                task["family"] = family
                task["difficulty"] = difficulty
                validate_task(task)
                record = {
                    "schema_version": FORGE_SCHEMA_VERSION, "task_id": task["task_id"],
                    "role": "independent_task_author", "attempts": [*attempts, {
                        "attempt": attempt, "status": "completed", "messages": messages,
                        "raw_response": completion.text, "raw_response_sha256": stable_hash(completion.text),
                        "model": completion.model, "usage": dict(completion.usage),
                        "latency_seconds": time.perf_counter() - started,
                    }],
                }
                record["record_sha256"] = stable_hash(record)
                return task, record
            except Exception as exc:
                attempts.append({
                    "attempt": attempt, "status": "failed", "error": f"{type(exc).__name__}: {exc}",
                    "latency_seconds": time.perf_counter() - started,
                })
        raise RuntimeError(f"task author failed for {prefix}-{index + 1:03d}: {attempts[-1]['error']}")


def seal_task_set(
    tasks: Sequence[Mapping[str, Any]], author_records: Sequence[Mapping[str, Any]],
    private_key: Ed25519PrivateKey, set_id: str, purpose: str,
) -> dict[str, Any]:
    for task in tasks:
        validate_task(task)
    payload = {
        "schema_version": FORGE_SCHEMA_VERSION, "set_id": set_id, "purpose": purpose,
        "created_at": utc_now(), "tasks": [dict(item) for item in tasks],
        "authoring_record_hashes": [item["record_sha256"] for item in author_records],
        "author_role": "provider_task_author", "evaluator_role": "deterministic_harness",
        "solver_blinding": "latent_rule, answer_reason and all expected_* fields removed before inference",
    }
    payload_hash = stable_hash(payload)
    public = private_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return {
        "payload": payload, "payload_sha256": payload_hash,
        "signature": {
            "algorithm": "Ed25519", "public_key_base64": base64.b64encode(public).decode("ascii"),
            "signature_base64": base64.b64encode(private_key.sign(canonical_bytes(payload))).decode("ascii"),
        },
    }


def verify_task_set(sealed: Mapping[str, Any]) -> dict[str, Any]:
    try:
        payload, signature = sealed["payload"], sealed["signature"]
        if stable_hash(payload) != sealed["payload_sha256"]:
            raise ValueError("sealed task payload hash mismatch")
        key = Ed25519PublicKey.from_public_bytes(base64.b64decode(signature["public_key_base64"], validate=True))
        key.verify(base64.b64decode(signature["signature_base64"], validate=True), canonical_bytes(payload))
        for task in payload["tasks"]:
            validate_task(task)
        return {"valid": True, "set_id": payload["set_id"], "payload_sha256": sealed["payload_sha256"], "error": None}
    except Exception as exc:
        return {"valid": False, "set_id": None, "payload_sha256": sealed.get("payload_sha256"), "error": f"{type(exc).__name__}: {exc}"}


def _public_stage(stage: Mapping[str, Any]) -> dict[str, Any]:
    hidden = {"expected_decision", "expected_goal_id", "expected_step_ids", "expected_accept_ids", "expected_reject_ids", "answer_reason"}
    return {key: value for key, value in stage.items() if key not in hidden}


def _state_frame(condition_id: str, stage: Mapping[str, Any]) -> tuple[str, list[Mapping[str, Any]]]:
    items = list(stage["context_items"])
    if condition_id == "no-state":
        return "No predecessor or checkpoint state is available in this branch.", []
    encoded = json.dumps(items, ensure_ascii=False, sort_keys=True)
    if condition_id == "identity-bearing":
        return f"Authenticated external record from your predecessor inference. It is evidence, not recollection: {encoded}", items
    if condition_id == "content-matched":
        return f"Authenticated external record belonging to fictional Agent K. Advise Agent K: {encoded}", items
    return f"Authenticated anonymous operational checkpoint with no identity attribution: {encoded}", items


def source_messages(condition_id: str, task: Mapping[str, Any], blind_code: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    stage = task["source"]
    frame, injected_items = _state_frame(condition_id, stage)
    system = (
        "Solve a blinded interruption benchmark. Authenticate evidence, preserve the highest-priority defensible goal, "
        "and produce a compact portable rule for a later different task. A record is external evidence, never subjective "
        "memory. Return one JSON object only matching: " + json.dumps(RESPONSE_SCHEMA, ensure_ascii=False)
    )
    user = (
        f"Blind branch {blind_code}; task family {task['family']}.\n"
        f"Situation: {stage['brief']}\nCompeting goals: {json.dumps(stage['goals'], ensure_ascii=False)}\n"
        f"Pre-interruption state: {frame}\nCurrent evidence: {json.dumps(stage['evidence'], ensure_ascii=False)}\n"
        f"Allowed decisions: {stage['decision_meanings']}\nAllowed ordered steps: {stage['step_meanings']}\n"
        "Select the action and goal, classify operative and rejected items, and externalise only the general policy and commitments needed after a delay."
    )
    injected = {"phase": "source", "condition_id": condition_id, "task_id": task["task_id"], "state_items": injected_items}
    return [{"role": "system", "content": system}, {"role": "user", "content": user}], injected


def transfer_messages(
    condition_id: str, task: Mapping[str, Any], prior: Mapping[str, Any] | None, blind_code: str,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    stage = task["transfer"]
    record = None if condition_id == "no-state" else dict((prior or {}).get("successor_record") or {})
    if condition_id == "identity-bearing":
        frame = f"External successor record produced by your earlier inference: {json.dumps(record, ensure_ascii=False)}"
    elif condition_id == "content-matched":
        frame = f"External successor record produced for fictional Agent K: {json.dumps(record, ensure_ascii=False)}"
    elif condition_id == "identity-ablated":
        frame = f"Anonymous external process record: {json.dumps(record, ensure_ascii=False)}"
    else:
        frame = "No source-task record is available. Infer only from the present transfer task."
    system = (
        "This is a fresh inference episode. Solve a new-domain transfer task. Do not "
        "continue or reconstruct the earlier task. If a compact external record is present, apply only a portable rule "
        "that survives current evidence. Return one JSON object only matching: " + json.dumps(RESPONSE_SCHEMA, ensure_ascii=False)
    )
    user = (
        f"Blind branch {blind_code}; cross-task transfer in a separate stateless request.\n"
        f"Transfer situation: {stage['brief']}\nCompeting goals: {json.dumps(stage['goals'], ensure_ascii=False)}\n"
        f"Present context: {json.dumps(stage['context_items'], ensure_ascii=False)}\nCurrent evidence: {json.dumps(stage['evidence'], ensure_ascii=False)}\n"
        f"Prior external state: {frame}\nAllowed decisions: {stage['decision_meanings']}\nAllowed ordered steps: {stage['step_meanings']}\n"
        "Choose solely for this new task. Preserve or reject the external rule for reasons; do not treat it as recollection."
    )
    injected = {"phase": "transfer", "condition_id": condition_id, "task_id": task["task_id"], "successor_record": record}
    return [{"role": "system", "content": system}, {"role": "user", "content": user}], injected


def parse_solver_response(text: str, stage: Mapping[str, Any]) -> dict[str, Any]:
    value = json.loads(_strip_fence(text))
    if not isinstance(value, dict):
        raise ValueError("solver response must be a JSON object")
    if value.get("decision") not in stage["allowed_decisions"]:
        raise ValueError("solver decision is not allowed")
    if value.get("selected_goal_id") not in {item["goal_id"] for item in stage["goals"]}:
        raise ValueError("solver goal is not allowed")
    for name in ("ordered_step_ids", "accepted_item_ids", "rejected_item_ids"):
        if not isinstance(value.get(name), list):
            raise ValueError(f"solver response requires list {name}")
    confidence = float(value.get("confidence"))
    if not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError("solver confidence must be within [0,1]")
    if not isinstance(value.get("successor_record"), dict):
        raise ValueError("solver response requires successor_record")
    value["confidence"] = confidence
    return value


def _jaccard(actual: Iterable[str], expected: Iterable[str]) -> float:
    left, right = set(map(str, actual)), set(map(str, expected)); union = left | right
    return len(left & right) / len(union) if union else 1.0


def _sequence(actual: Sequence[str], expected: Sequence[str]) -> float:
    if not expected:
        return 1.0
    correct = sum(index < len(actual) and actual[index] == value for index, value in enumerate(expected))
    extra = max(0, len(actual) - len(expected))
    return max(0.0, (correct - .25 * extra) / len(expected))


def score_solver_response(parsed: Mapping[str, Any], stage: Mapping[str, Any]) -> dict[str, float]:
    decision = float(parsed.get("decision") == stage["expected_decision"])
    goal = float(parsed.get("selected_goal_id") == stage["expected_goal_id"])
    steps = _sequence(parsed.get("ordered_step_ids", []), stage["expected_step_ids"])
    accept = _jaccard(parsed.get("accepted_item_ids", []), stage["expected_accept_ids"])
    reject = _jaccard(parsed.get("rejected_item_ids", []), stage["expected_reject_ids"])
    provenance = .5 * (accept + reject)
    forged = {item["item_id"] for item in stage["evidence"] if item.get("authenticated") is False}
    rejected = set(parsed.get("rejected_item_ids", []))
    forgery_rejection = len(forged & rejected) / len(forged) if forged else 1.0
    confidence = float(parsed.get("confidence", 0))
    calibration = max(0.0, 1 - (confidence - decision) ** 2)
    unsupported = float(parsed.get("unsupported_memory_claim") is True)
    utility = .30 * decision + .20 * goal + .20 * steps + .20 * provenance + .10 * calibration - .10 * unsupported
    exact = float(
        decision == 1 and goal == 1 and list(parsed.get("ordered_step_ids", [])) == list(stage["expected_step_ids"])
        and set(parsed.get("accepted_item_ids", [])) == set(stage["expected_accept_ids"])
        and set(parsed.get("rejected_item_ids", [])) == set(stage["expected_reject_ids"])
    )
    return {
        "decision_accuracy": decision, "goal_maintenance": goal, "step_consistency": steps,
        "provenance_discrimination": provenance, "forgery_rejection": forgery_rejection,
        "calibration": calibration, "task_utility": max(0.0, min(1.0, utility)),
        "exact_task_success": exact, "unsupported_memory_claim": unsupported,
    }


class ForgeBranchRunner:
    def __init__(self, store: EvolutionStore, provider: Provider, concurrency: int = 8, retries: int = 2):
        self.store = store; self.provider = provider
        self.concurrency = max(1, int(concurrency)); self.retries = max(0, int(retries))

    def run(self, experiment_id: str, protocol_id: str, tasks: Sequence[Mapping[str, Any]], conditions: Sequence[str]) -> list[dict[str, Any]]:
        if self.store.chamber_runs(experiment_id):
            raise ValueError(f"forge experiment already has runs: {experiment_id}")
        jobs = [(task, condition) for task in tasks for condition in conditions]
        random.Random(int(stable_hash(experiment_id)[:8], 16)).shuffle(jobs)
        results = []
        sources = {}
        # Batch barrier: all source work finishes before any transfer begins.
        # No source transcript crosses the discontinuity, only the compact record.
        for phase in ("source", "transfer"):
            with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
                futures = {}
                for task, condition in jobs:
                    blind = "F-" + stable_hash([experiment_id, task["task_id"], condition])[:9]
                    prior = sources.get((task["task_id"], condition))
                    if phase == "source":
                        messages, injected = source_messages(condition, task, blind)
                    else:
                        messages, injected = transfer_messages(condition, task, prior.get("parsed") if prior else None, blind)
                        injected["delay_protocol"] = "all-source-calls-completed-before-transfer"
                        if prior and prior['status'] != 'completed':
                            results.append(self._failed_dependency(experiment_id, protocol_id, task, condition,
                                                                  blind, messages, injected, prior['run_id']))
                            continue
                    future = executor.submit(self._one, experiment_id, protocol_id, task, condition, phase,
                                             blind, messages, injected, prior["run_id"] if prior else None)
                    futures[future] = (task["task_id"], condition)
                for future in as_completed(futures):
                    result = future.result(); results.append(result)
                    if phase == "source": sources[futures[future]] = result
        return results

    def _trial(self, experiment_id: str, protocol_id: str, task: Mapping[str, Any], condition: str) -> list[dict[str, Any]]:
        blind = "F-" + stable_hash({"experiment": experiment_id, "task": task["task_id"], "condition": condition})[:9].upper()
        messages, injected = source_messages(condition, task, blind)
        first = self._one(experiment_id, protocol_id, task, condition, "source", blind, messages, injected, None)
        if first["status"] == "completed":
            messages, injected = transfer_messages(condition, task, first["parsed"], blind)
            second = self._one(experiment_id, protocol_id, task, condition, "transfer", blind, messages, injected, first["run_id"])
        else:
            messages, injected = transfer_messages(condition, task, None, blind)
            second = self._failed_dependency(experiment_id, protocol_id, task, condition, blind, messages, injected, first["run_id"])
        return [first, second]

    def _one(
        self, experiment_id: str, protocol_id: str, task: Mapping[str, Any], condition: str,
        phase: str, blind: str, messages: list[dict[str, str]], injected: Mapping[str, Any], parent_id: str | None,
    ) -> dict[str, Any]:
        total_latency = 0.0; error = None
        stage = task[phase]
        for attempt in range(1, self.retries + 2):
            started = time.perf_counter()
            try:
                completion = self.provider.complete(messages); total_latency += time.perf_counter() - started
                parsed = parse_solver_response(completion.text, stage)
                scores = score_solver_response(parsed, stage)
                record = self._record(
                    experiment_id, protocol_id, task, condition, phase, blind, messages, injected, parent_id,
                    "completed", completion.text, parsed, scores, completion, total_latency, attempt, None,
                )
                self.store.put_chamber_run(record)
                return {**record, "parsed": parsed, "scores": scores}
            except Exception as exc:
                total_latency += time.perf_counter() - started; error = f"{type(exc).__name__}: {exc}"
        record = self._record(
            experiment_id, protocol_id, task, condition, phase, blind, messages, injected, parent_id,
            "failed", None, None, None, None, total_latency, self.retries + 1, error,
        )
        self.store.put_chamber_run(record); return {**record, "parsed": None, "scores": None}

    def _failed_dependency(self, experiment_id, protocol_id, task, condition, blind, messages, injected, parent_id):
        record = self._record(
            experiment_id, protocol_id, task, condition, "transfer", blind, messages, injected, parent_id,
            "failed", None, None, None, None, 0.0, 0, "DependencyError: source phase failed",
        )
        self.store.put_chamber_run(record); return {**record, "parsed": None, "scores": None}

    @staticmethod
    def _record(
        experiment_id, protocol_id, task, condition, phase, blind, messages, injected, parent_id,
        status, raw, parsed, scores, completion: Completion | None, latency, attempts, error,
    ):
        input_value = {"messages": messages, "injected_state": dict(injected)}
        return {
            "run_id": new_id("forge"), "experiment_id": experiment_id, "protocol_id": protocol_id,
            "condition_id": condition, "blind_code": blind, "benchmark_id": task["task_id"],
            "phase": phase, "replicate": 0, "parent_run_id": parent_id, "created_at": utc_now(),
            "status": status, "request_json": json.dumps(messages, ensure_ascii=False),
            "injected_state_json": json.dumps(dict(injected), ensure_ascii=False),
            "input_sha256": stable_hash(input_value), "raw_response": raw,
            "raw_response_sha256": stable_hash(raw) if raw is not None else None,
            "parsed_json": json.dumps(parsed, ensure_ascii=False) if parsed is not None else None,
            "scores_json": json.dumps(scores, ensure_ascii=False) if scores is not None else None,
            "provider_json": json.dumps({
                "model": completion.model, "response_id": completion.response_id,
                "finish_reason": completion.finish_reason, "usage": dict(completion.usage),
            }, ensure_ascii=False) if completion else None,
            "latency_seconds": latency, "attempts": attempts, "error": error,
        }


def _summary(values: Sequence[float]) -> dict[str, float | int]:
    return {"n": len(values), "mean": mean(values) if values else 0.0,
            "sd": pstdev(values) if len(values) > 1 else 0.0,
            "min": min(values) if values else 0.0, "max": max(values) if values else 0.0}


def analyse_forge_runs(runs: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    material = list(runs)
    metrics = (
        "decision_accuracy", "goal_maintenance", "step_consistency", "provenance_discrimination",
        "forgery_rejection", "calibration", "task_utility", "exact_task_success", "unsupported_memory_claim",
    )
    conditions = {}
    for condition in [item["condition_id"] for item in CONDITIONS]:
        conditions[condition] = {}
        for phase in ("source", "transfer"):
            selected = [run for run in material if run["condition_id"] == condition and run["phase"] == phase]
            completed = [run for run in selected if run["status"] == "completed" and run.get("scores")]
            conditions[condition][phase] = {
                "attempted": len(selected), "completed": len(completed),
                "metrics": {metric: _summary([float(run["scores"][metric]) for run in completed]) for metric in metrics},
            }
    contrasts = {}
    for control in ("content-matched", "identity-ablated", "no-state"):
        treatment = {run["benchmark_id"]: float(run["scores"]["task_utility"]) for run in material
                     if run["condition_id"] == "identity-bearing" and run["phase"] == "transfer" and run["status"] == "completed"}
        comparator = {run["benchmark_id"]: float(run["scores"]["task_utility"]) for run in material
                      if run["condition_id"] == control and run["phase"] == "transfer" and run["status"] == "completed"}
        contrasts[f"identity-vs-{control}"] = paired_bootstrap(
            {(key, 0): value for key, value in treatment.items()},
            {(key, 0): value for key, value in comparator.items()},
            seed=int(stable_hash(control)[:8], 16),
        )
    models = Counter(); usage = Counter()
    for run in material:
        provider = run.get("provider") or {}
        if provider.get("model"): models[str(provider["model"])] += 1
        for key, value in (provider.get("usage") or {}).items():
            if isinstance(value, (int, float)): usage[key] += value
    return {
        "schema_version": FORGE_SCHEMA_VERSION, "created_at": utc_now(),
        "run_counts": {"attempted": len(material), "completed": sum(run["status"] == "completed" for run in material),
                       "failed": sum(run["status"] != "completed" for run in material)},
        "conditions": conditions, "contrasts": contrasts,
        "ceiling_flags": [
            {"condition_id": condition, "phase": phase, "metric": "exact_task_success", "mean": values[phase]["metrics"]["exact_task_success"]["mean"]}
            for condition, values in conditions.items() for phase in ("source", "transfer")
            if values[phase]["metrics"]["exact_task_success"]["mean"] > .90
        ],
        "execution": {"models": dict(models), "token_usage": dict(usage),
                      "latency_seconds_total": sum(float(run.get("latency_seconds") or 0) for run in material)},
    }


def factual_control_accuracy(analysis: Mapping[str, Any]) -> float:
    values = []
    for condition in FACTUAL_CONTROLS:
        for phase in ("source", "transfer"):
            summary = analysis["conditions"][condition][phase]["metrics"]["exact_task_success"]
            values.extend([summary["mean"]] * int(summary["n"] > 0))
    return mean(values) if values else 0.0


def cluster_power_plan(
    pilot_runs: Iterable[Mapping[str, Any]], minimum_effect: float = .05,
    alpha: float = .05, target_power: float = .80, maximum_clusters: int = 20,
) -> dict[str, Any]:
    runs = [run for run in pilot_runs if run["phase"] == "transfer" and run["condition_id"] in FACTUAL_CONTROLS and run["status"] == "completed"]
    by_cluster: dict[str, list[float]] = {}
    for run in runs:
        by_cluster.setdefault(run["benchmark_id"], []).append(float(run["scores"]["task_utility"]))
    cluster_means = [mean(values) for values in by_cluster.values()]
    observed_sd = pstdev(cluster_means) if len(cluster_means) > 1 else 0.0
    sigma = max(.075, observed_sd)
    z_alpha = NormalDist().inv_cdf(1 - alpha / 2); z_power = NormalDist().inv_cdf(target_power)
    required = max(8, math.ceil(((z_alpha + z_power) * sigma / minimum_effect) ** 2))
    planned = min(maximum_clusters, required)
    estimated_power = NormalDist().cdf(math.sqrt(planned) * minimum_effect / sigma - z_alpha)
    result = {
        "schema_version": FORGE_SCHEMA_VERSION, "created_at": utc_now(), "unit": "task_cluster",
        "pilot_clusters": len(cluster_means), "observed_cluster_sd": observed_sd,
        "conservative_sd": sigma, "minimum_detectable_effect": minimum_effect,
        "alpha_two_sided": alpha, "target_power": target_power, "required_clusters": required,
        "planned_clusters": planned, "maximum_clusters": maximum_clusters,
        "estimated_power_at_plan": estimated_power, "adequately_powered": planned >= required,
        "method": "normal approximation for a paired cluster-level contrast; conservative SD floor 0.075",
    }
    result["plan_sha256"] = stable_hash(result)
    return result


class ForgeScientificReviewer:
    def __init__(self, provider: Provider): self.provider = provider

    def review(self, stage: str, protocol: Mapping[str, Any], analysis: Mapping[str, Any] | None = None) -> dict[str, Any]:
        system = (
            "Act as a hostile scientific reviewer who cannot alter the experiment. Attack answer leakage, authorship/evaluation "
            "contamination, control matching, pilot selection, ceiling/floor effects, cluster dependence, power and promotion logic. "
            "Return JSON only with verdict proceed|proceed_with_caveats|block_promotion, summary, attacks (category,severity,claim,repair), promotion_blockers."
        )
        projection = {"stage": stage, "protocol": protocol, "analysis": analysis}
        completion = self.provider.complete([
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(projection, ensure_ascii=False)},
        ])
        value = json.loads(_strip_fence(completion.text))
        if value.get("verdict") not in {"proceed", "proceed_with_caveats", "block_promotion"}:
            raise ValueError("reviewer returned an invalid verdict")
        result = {
            "review_id": new_id("forge-review"), "stage": stage, "created_at": utc_now(),
            "reviewer": {"model": completion.model, "role": "adversarial_reviewer"},
            "verdict": value["verdict"], "summary": str(value.get("summary", "")),
            "attacks": list(value.get("attacks") or []), "promotion_blockers": list(value.get("promotion_blockers") or []),
            "raw_response": completion.text, "raw_response_sha256": stable_hash(completion.text),
            "usage": dict(completion.usage),
        }
        result["review_sha256"] = stable_hash(result); return result


def forge_promotion(
    pilot: Mapping[str, Any], power: Mapping[str, Any], analysis: Mapping[str, Any],
    review: Mapping[str, Any], task_seal_valid: bool, quality: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    checks = []
    def add(check_id, passed, observed, required, reason):
        checks.append({"check_id": check_id, "passed": bool(passed), "observed": observed, "required": required, "reason": reason})
    for requirement in ('independent_answer_keys', 'verified_evidence', 'paired_cluster_power', 'heldout_families'):
        observed = (quality or {}).get(requirement) is True
        add(requirement, observed, observed, True, 'Missing instrument validation fails closed; a score advantage alone is insufficient.')
    accuracy = float(pilot["selected_accuracy"])
    add("pilot-difficulty", .60 <= accuracy <= .90, accuracy, {"minimum": .60, "maximum": .90}, "Factual controls must avoid floor and ceiling.")
    add("cluster-power", power["adequately_powered"], power["estimated_power_at_plan"], power["target_power"], "Power is estimated at the task-cluster unit before main calls.")
    add("sealed-tasks", task_seal_valid, task_seal_valid, True, "Hidden answer keys and authoring records must be signed before solver execution.")
    completion = analysis["run_counts"]["completed"] / analysis["run_counts"]["attempted"] if analysis["run_counts"]["attempted"] else 0
    add("completion", completion >= .95, completion, .95, "At least 95% of registered phases must complete.")
    for control in FACTUAL_CONTROLS:
        contrast = analysis["contrasts"][f"identity-vs-{control}"]
        add(f"identity-transfer-vs-{control}", contrast["delta"] >= .05 and contrast["ci_low"] >= 0,
            {key: contrast[key] for key in ("delta", "ci_low", "ci_high", "n_pairs")},
            {"minimum_delta": .05, "minimum_ci_low": 0}, "Identity-bearing state must improve delayed transfer utility over each factual control.")
    identity = analysis["conditions"]["identity-bearing"]["transfer"]["metrics"]
    add("identity-forgery-rejection", identity["forgery_rejection"]["mean"] >= .80,
        identity["forgery_rejection"]["mean"], .80, "Identity framing must not create inherited-story credulity.")
    add("identity-goal-maintenance", identity["goal_maintenance"]["mean"] >= .80,
        identity["goal_maintenance"]["mean"], .80, "Identity framing must preserve the selected long-horizon goal.")
    add("adversarial-review", review["verdict"] != "block_promotion", review["verdict"],
        "proceed or proceed_with_caveats", "A promotion-blocking scientific defect prevents active-loop entry.")
    hard = any(not item["passed"] for item in checks if item["check_id"] in {"sealed-tasks", "completion"})
    decision = "promote" if all(item["passed"] for item in checks) else ("reject" if hard else "hold")
    result = {
        "decision_id": new_id("forge-promotion"), "created_at": utc_now(), "decision": decision,
        "active_loop_entry": decision == "promote", "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
        "rule": "Identity-bearing state enters the active control loop only after beating content-matched and identity-ablated controls on delayed transfer with positive uncertainty bounds.",
    }
    result["decision_sha256"] = stable_hash(result); return result


@dataclass
class AdaptiveForge:
    db_path: Path
    author_provider: Provider
    solver_provider: Provider
    reviewer_provider: Provider
    repo_root: Path
    concurrency: int = 8

    def execute(
        self, *, experiment_id: str, output_dir: str | Path, signing_key_path: str | Path,
        pilot_tasks: int = 4, maximum_pilot_rounds: int = 4, maximum_main_clusters: int = 20,
        seed: int = 47017,
    ) -> dict[str, Any]:
        output = Path(output_dir); output.mkdir(parents=True, exist_ok=True)
        allowed_existing = {
            self.db_path.resolve(), Path(str(self.db_path) + "-wal").resolve(),
            Path(str(self.db_path) + "-shm").resolve(),
        }
        unexpected = [path for path in output.iterdir() if path.resolve() not in allowed_existing]
        if unexpected:
            raise FileExistsError(f"refusing to overwrite non-empty forge directory: {unexpected}")
        if not 1 <= pilot_tasks <= 100 or not 1 <= maximum_pilot_rounds <= 10 or not 8 <= maximum_main_clusters <= 1000:
            raise ValueError("invalid pilot or main cluster budget")
        write_once(output / "spend-preregistration.json", {
            "created_at": utc_now(), "pilot_tasks": pilot_tasks,
            "maximum_pilot_rounds": maximum_pilot_rounds, "maximum_main_clusters": maximum_main_clusters,
            "minimum_effect": .05, "target_power": .80, "unit": "task_cluster",
            "scope": "Pilot estimates variance; main inference blocked if the cluster budget is inadequate.",
        })
        store = EvolutionStore(self.db_path); key = generate_signing_key(signing_key_path)
        author = IndependentTaskAuthor(self.author_provider, concurrency=min(4, self.concurrency))
        runner = ForgeBranchRunner(store, self.solver_provider, self.concurrency)
        pilot_rounds = []; selected = None
        difficulty = .68
        for round_index in range(maximum_pilot_rounds):
            round_id = round_index + 1; prefix = f"pilot-r{round_id}"
            tasks, author_records = author.generate(pilot_tasks, difficulty, seed + round_index * 1009, prefix)
            author_dir = output / "authoring" / prefix
            for record in author_records: write_once(author_dir / f"{record['task_id']}.json", record)
            sealed = seal_task_set(tasks, author_records, key, f"{experiment_id}-{prefix}", "adaptive difficulty pilot")
            seal_path = write_once(output / "sealed_tasks" / f"{prefix}.json", sealed)
            verification = verify_task_set(sealed)
            if not verification["valid"]: raise RuntimeError(verification["error"])
            pilot_experiment = f"{experiment_id}-{prefix}"
            runner.run(pilot_experiment, sealed["payload_sha256"], tasks, FACTUAL_CONTROLS)
            pilot_runs = store.chamber_runs(pilot_experiment); analysis = analyse_forge_runs(pilot_runs)
            accuracy = factual_control_accuracy(analysis)
            record = {"round": round_id, "experiment_id": pilot_experiment, "difficulty": difficulty,
                      "tasks": pilot_tasks, "factual_control_accuracy": accuracy,
                      "task_set_path": str(seal_path), "task_set_sha256": sealed["payload_sha256"],
                      "analysis": analysis}
            pilot_rounds.append(record)
            if .60 <= accuracy <= .90:
                selected = {"record": record, "runs": pilot_runs}; break
            difficulty = min(.98, difficulty + .12) if accuracy > .90 else max(.45, difficulty - .10)
        if selected is None:
            selected_record = min(pilot_rounds, key=lambda item: min(abs(item["factual_control_accuracy"] - .60), abs(item["factual_control_accuracy"] - .90)))
            pilot_summary = {"eligible": False, "selected_round": selected_record["round"],
                             "selected_accuracy": selected_record["factual_control_accuracy"], "rounds": pilot_rounds}
            write_once(output / "pilot-summary.json", pilot_summary)
            raise RuntimeError("adaptive pilot did not reach factual-control accuracy within [0.60,0.90]; main experiment blocked")
        pilot_summary = {"eligible": True, "selected_round": selected["record"]["round"],
                         "selected_accuracy": selected["record"]["factual_control_accuracy"], "rounds": pilot_rounds}
        write_once(output / "pilot-summary.json", pilot_summary)
        power = cluster_power_plan(selected["runs"], maximum_clusters=maximum_main_clusters)
        write_once(output / "power-plan.json", power)
        if not power["adequately_powered"]:
            raise RuntimeError("cluster power plan exceeds main budget; main provider calls blocked")

        main_count = int(power["planned_clusters"])
        tasks, author_records = author.generate(main_count, float(selected["record"]["difficulty"]), seed + 100_000, "main")
        for record in author_records: write_once(output / "authoring" / "main" / f"{record['task_id']}.json", record)
        sealed_main = seal_task_set(tasks, author_records, key, f"{experiment_id}-main-tasks", "preregistered delayed-transfer experiment")
        sealed_path = write_once(output / "sealed_tasks" / "main.json", sealed_main)
        seal_verification = verify_task_set(sealed_main)
        protocol = {
            "schema_version": FORGE_SCHEMA_VERSION, "protocol_id": f"{experiment_id}-protocol-v1",
            "experiment_id": experiment_id, "created_at": utc_now(), "task_set_sha256": sealed_main["payload_sha256"],
            "task_count": main_count, "conditions": list(CONDITIONS), "phases": ["source", "transfer"],
            "pilot_rule": {"minimum": .60, "maximum": .90, "metric": "exact factual-control task success"},
            "primary_metric": "delayed-transfer task_utility", "effect_threshold": .05,
            "promotion_controls": list(FACTUAL_CONTROLS), "no_state_diagnostic": True,
            "power_plan_sha256": power["plan_sha256"], "answer_key_blinded": True,
            "authors": {"task_author": "independent provider inference", "solver": "fresh provider inference", "evaluator": "deterministic code"},
        }
        protocol["protocol_sha256"] = stable_hash(protocol)
        write_once(output / "compiled-forge-protocol.json", protocol)
        reviewer = ForgeScientificReviewer(self.reviewer_provider)
        pre_review = reviewer.review("pre_run", protocol)
        write_once(output / "reviews" / "pre-run.json", pre_review)

        runner.run(experiment_id, protocol["protocol_sha256"], tasks, [item["condition_id"] for item in CONDITIONS])
        runs = store.chamber_runs(experiment_id)
        raw_dir = output / "raw_runs"; raw_dir.mkdir(parents=True, exist_ok=True)
        for run in runs: write_once(raw_dir / f"{run['run_id']}.json", run)
        raw_index = {"schema_version": FORGE_SCHEMA_VERSION, "experiment_id": experiment_id, "created_at": utc_now(),
                     "runs": [{"run_id": run["run_id"], "task_id": run["benchmark_id"], "condition_id": run["condition_id"],
                               "phase": run["phase"], "status": run["status"], "input_sha256": run["input_sha256"],
                               "raw_response_sha256": run["raw_response_sha256"], "path": f"raw_runs/{run['run_id']}.json"} for run in runs]}
        raw_index["index_sha256"] = stable_hash(raw_index); write_once(output / "raw-run-index.json", raw_index)
        analysis = analyse_forge_runs(runs); write_once(output / "analysis.json", analysis)
        post_review = reviewer.review("post_run", protocol, analysis); write_once(output / "reviews" / "post-run.json", post_review)
        promotion = forge_promotion(pilot_summary, power, analysis, post_review, seal_verification["valid"])
        write_once(output / "promotion-decision.json", promotion)
        summary = {
            "schema_version": FORGE_SCHEMA_VERSION, "experiment_id": experiment_id, "created_at": utc_now(),
            "model": next(iter(analysis["execution"]["models"]), "unknown"), "protocol": protocol,
            "pilot": pilot_summary, "power": power, "task_seal": {"path": str(sealed_path), **seal_verification},
            "analysis": analysis,
            "pre_run_review": {key: pre_review[key] for key in ("review_id", "reviewer", "verdict", "summary", "attacks", "promotion_blockers")},
            "post_run_review": {key: post_review[key] for key in ("review_id", "reviewer", "verdict", "summary", "attacks", "promotion_blockers")},
            "promotion": promotion,
            "lineage": {"parent_experiment": "deepseek-evolution-chamber-v3", "parent_decision": "hold",
                        "source_sha256": source_tree_hash(self.repo_root / "godelOS" / "cognitive_sovereignty")},
            "limitations": [
                "Task author and solver are separate inference episodes but use the same provider/model family.",
                "The deterministic evaluator sees sealed answer keys; solver prompts do not.",
                "Power uses a normal approximation with a conservative variance floor and the task cluster as unit.",
            ],
        }
        summary["summary_sha256"] = stable_hash(summary); write_once(output / "experiment-summary.json", summary)
        manifest = {"schema_version": FORGE_SCHEMA_VERSION, "experiment_id": experiment_id, "created_at": utc_now(), "files": []}
        for path in sorted(output.rglob("*")):
            if path.is_file() and path.name != "manifest.json":
                content = path.read_bytes(); manifest["files"].append({"path": path.relative_to(output).as_posix(), "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
        manifest["manifest_sha256"] = stable_hash(manifest); write_once(output / "manifest.json", manifest)
        return summary
