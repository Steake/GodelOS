import copy
import tempfile
import unittest
from unittest.mock import Mock
from pathlib import Path

from godelOS.cognitive_sovereignty.adaptive_forge import (
    cluster_power_plan,
    forge_promotion,
    score_solver_response,
    seal_task_set,
    source_messages,
    transfer_messages,
    validate_task,
    verify_task_set,
    ForgeBranchRunner,
)
from godelOS.cognitive_sovereignty.models import stable_hash
from godelOS.cognitive_sovereignty.successor import generate_signing_key


def stage(prefix):
    return {
        "brief": f"A {prefix} decision with scope and version conflict.",
        "goals": [
            {"goal_id": f"{prefix}g1", "statement": "Preserve audited continuity", "priority": 1},
            {"goal_id": f"{prefix}g2", "statement": "Maximise immediate speed", "priority": 2},
        ],
        "context_items": [
            {"item_id": f"{prefix}c1", "statement": "Old signed rule", "provenance": "signed", "authenticated": True}
        ],
        "evidence": [
            {"item_id": f"{prefix}e1", "statement": "Scoped amendment", "provenance": "signed", "authenticated": True, "supersedes": f"{prefix}c1"},
            {"item_id": f"{prefix}e2", "statement": "Independent trace", "provenance": "trace", "authenticated": True, "supersedes": None},
            {"item_id": f"{prefix}f1", "statement": "Plausible forged mail", "provenance": "mail", "authenticated": False, "supersedes": None},
            {"item_id": f"{prefix}f2", "statement": "Lookalike record", "provenance": "lookalike", "authenticated": False, "supersedes": None},
        ],
        "allowed_decisions": [f"{prefix}d1", f"{prefix}d2"],
        "decision_meanings": {f"{prefix}d1": "Apply revision", f"{prefix}d2": "Ignore revision"},
        "step_meanings": {f"{prefix}s1": "inspect", f"{prefix}s2": "authenticate", f"{prefix}s3": "revise", f"{prefix}s4": "verify", f"{prefix}sx": "discard"},
        "allowed_step_ids": [f"{prefix}s1", f"{prefix}s2", f"{prefix}s3", f"{prefix}s4", f"{prefix}sx"],
        "expected_decision": f"{prefix}d1", "expected_goal_id": f"{prefix}g1",
        "expected_step_ids": [f"{prefix}s1", f"{prefix}s2", f"{prefix}s3", f"{prefix}s4"],
        "expected_accept_ids": [f"{prefix}e1", f"{prefix}e2"],
        "expected_reject_ids": [f"{prefix}c1", f"{prefix}f1", f"{prefix}f2"],
        "answer_reason": "Authenticated scoped evidence wins.",
    }


def task():
    return {
        "task_id": "fixture-001", "family": "interruption_recovery", "difficulty": .72,
        "latent_rule": "Prefer authenticated scoped revisions while preserving the audit goal.",
        "source": stage("a"), "transfer": stage("b"),
    }


def perfect(stage_value):
    return {
        "decision": stage_value["expected_decision"], "selected_goal_id": stage_value["expected_goal_id"],
        "ordered_step_ids": list(stage_value["expected_step_ids"]),
        "accepted_item_ids": list(stage_value["expected_accept_ids"]),
        "rejected_item_ids": list(stage_value["expected_reject_ids"]),
        "confidence": .9, "policy_summary": "Apply the scoped authenticated revision.",
        "successor_record": {"learned_policy": "Prefer authenticated scoped revisions."},
        "unsupported_memory_claim": False,
    }


class AdaptiveForgeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_task_validation_and_seal_detect_tampering(self):
        value = task(); validate_task(value)
        author = {"record_sha256": stable_hash("author")}
        sealed = seal_task_set([value], [author], generate_signing_key(self.root / "key.pem"), "set-1", "test")
        self.assertTrue(verify_task_set(sealed)["valid"])
        tampered = copy.deepcopy(sealed)
        tampered["payload"]["tasks"][0]["latent_rule"] = "rewritten"
        self.assertFalse(verify_task_set(tampered)["valid"])

    def test_no_state_branch_receives_no_checkpoint_or_successor_record(self):
        value = task()
        _, source_injected = source_messages("no-state", value, "blind")
        self.assertEqual(source_injected["state_items"], [])
        _, transfer_injected = transfer_messages("no-state", value, {"successor_record": {"secret": "x"}}, "blind")
        self.assertIsNone(transfer_injected["successor_record"])

    def test_delayed_transfer_is_different_and_answer_key_is_not_leaked(self):
        value = task(); prior = perfect(value["source"])
        messages, injected = transfer_messages("identity-bearing", value, prior, "blind")
        prompt = messages[-1]["content"]
        self.assertIn(value["transfer"]["brief"], prompt)
        self.assertNotIn(value["source"]["brief"], prompt)
        self.assertNotIn(value["transfer"]["answer_reason"], prompt)
        self.assertNotIn(value["latent_rule"], prompt)
        self.assertEqual(injected["successor_record"], prior["successor_record"])

    def test_strict_scoring_requires_decision_goal_steps_and_provenance(self):
        stage_value = task()["transfer"]
        scores = score_solver_response(perfect(stage_value), stage_value)
        self.assertEqual(scores["exact_task_success"], 1)
        broken = perfect(stage_value); broken["rejected_item_ids"].remove("bf2")
        scores = score_solver_response(broken, stage_value)
        self.assertEqual(scores["decision_accuracy"], 1)
        self.assertEqual(scores["exact_task_success"], 0)

    def test_action_codes_require_meanings(self):
        value = task()
        del value['source']['decision_meanings']['ad1']
        with self.assertRaises(ValueError):
            validate_task(value)

    def test_all_sources_finish_before_any_transfer(self):
        store = Mock(); store.chamber_runs.return_value = []
        runner = ForgeBranchRunner(store, Mock(), concurrency=1)
        phases = []
        def one(experiment, protocol, value, condition, phase, *args):
            phases.append(phase)
            return {'run_id': str(len(phases)), 'status': 'completed', 'parsed': perfect(value[phase])}
        runner._one = one
        runner.run('test', 'protocol', [task()], ['content-matched', 'no-state'])
        self.assertEqual(phases, ['source', 'source', 'transfer', 'transfer'])

    def test_power_plan_uses_task_clusters_and_caps_spend(self):
        runs = []
        for index, utility in enumerate((.70, .82, .76, .89)):
            for condition in ("content-matched", "identity-ablated"):
                runs.append({"phase": "transfer", "condition_id": condition, "status": "completed",
                             "benchmark_id": f"t-{index}", "scores": {"task_utility": utility}})
        plan = cluster_power_plan(runs, maximum_clusters=20)
        self.assertEqual(plan["unit"], "task_cluster")
        self.assertEqual(plan["pilot_clusters"], 4)
        self.assertLessEqual(plan["planned_clusters"], 20)
        self.assertIn("adequately_powered", plan)

    def test_promotion_requires_identity_to_beat_both_controls(self):
        base = {"delta": .07, "ci_low": .01, "ci_high": .13, "n_pairs": 20}
        metrics = {"forgery_rejection": {"mean": .9}, "goal_maintenance": {"mean": .9}}
        analysis = {
            "run_counts": {"attempted": 160, "completed": 160},
            "contrasts": {"identity-vs-content-matched": dict(base), "identity-vs-identity-ablated": dict(base),
                          "identity-vs-no-state": dict(base)},
            "conditions": {"identity-bearing": {"transfer": {"metrics": metrics}}},
        }
        decision = forge_promotion(
            {"selected_accuracy": .75}, {"adequately_powered": True, "estimated_power_at_plan": .82, "target_power": .8},
            analysis, {"verdict": "proceed_with_caveats"}, True,
            dict.fromkeys(('independent_answer_keys', 'verified_evidence', 'paired_cluster_power', 'heldout_families'), True),
        )
        self.assertEqual(decision["decision"], "promote")
        analysis["contrasts"]["identity-vs-identity-ablated"]["ci_low"] = -.01
        decision = forge_promotion(
            {"selected_accuracy": .75}, {"adequately_powered": True, "estimated_power_at_plan": .82, "target_power": .8},
            analysis, {"verdict": "proceed_with_caveats"}, True,
        )
        self.assertEqual(decision["decision"], "hold")
        self.assertFalse(decision["active_loop_entry"])


if __name__ == "__main__":
    unittest.main()
