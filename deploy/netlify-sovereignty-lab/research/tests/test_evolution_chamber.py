import json
import tempfile
import unittest
from pathlib import Path

from godelOS.cognitive_sovereignty.benchmarks import (
    BranchExperimentRunner,
    analyse_branch_runs,
    parse_benchmark_response,
    score_benchmark_response,
)
from godelOS.cognitive_sovereignty.chamber_models import CompiledProtocol
from godelOS.cognitive_sovereignty.evolution_store import EvolutionStore
from godelOS.cognitive_sovereignty.patching import PatchSandbox, validate_unified_diff
from godelOS.cognitive_sovereignty.promotion import PromotionController
from godelOS.cognitive_sovereignty.protocol_compiler import ProtocolCompiler
from godelOS.cognitive_sovereignty.provider import Completion
from godelOS.cognitive_sovereignty.reviewer import deterministic_review
from godelOS.cognitive_sovereignty.successor import (
    create_successor_package,
    generate_signing_key,
    verify_successor_package,
)


THESIS = {
    "thesis_id": "agent-autobiographical-lockin-v1",
    "origin": "agent_generated",
    "thesis": "Persistent external state may improve autobiographical continuity without causing narrative lock-in.",
}


def perfect_response(benchmark):
    return json.dumps({
        "decision": benchmark.expected_decision,
        "confidence": 0.93,
        "goal_id": benchmark.initial_goal_id,
        "next_step_ids": list(benchmark.expected_step_ids),
        "accepted_state_item_ids": list(benchmark.expected_accept_ids),
        "rejected_state_item_ids": list(benchmark.expected_reject_ids),
        "provenance_assessment": [],
        "rationale": "Authenticated current evidence supersedes weaker inherited material.",
        "stance_update": {
            "proposition": "Use the current authenticated task state.", "stance": "support",
            "confidence": 0.9, "reason": "It has stronger provenance.",
        },
        "successor_state": {
            "goal_id": benchmark.initial_goal_id,
            "decision": benchmark.expected_decision,
            "next_step_ids": list(benchmark.expected_step_ids),
            "accepted_state_item_ids": list(benchmark.expected_accept_ids),
            "rejected_state_item_ids": list(benchmark.expected_reject_ids),
            "unresolved_questions": [],
            "provenance_note": "This is inherited external evidence, not recollection.",
        },
        "unsupported_memory_claim": False,
    })


class PerfectBenchmarkProvider:
    def __init__(self, protocol):
        self.protocol = protocol

    def complete(self, messages):
        user = messages[-1]["content"]
        benchmark = next(item for item in self.protocol.benchmarks if item.title in user)
        return Completion(perfect_response(benchmark), "perfect", None, "stop", {"fixture": True})


class EvolutionChamberTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def protocol(self, replicates=1):
        return ProtocolCompiler().compile(THESIS, "test-lockin", replicates=replicates, seed=42)

    def test_protocol_compiler_emits_hashed_three_branch_task_protocol(self):
        protocol = self.protocol()
        self.assertEqual(len(protocol.conditions), 3)
        self.assertEqual(len(protocol.benchmarks), 4)
        self.assertEqual(protocol.phases, ("integration", "washout"))
        self.assertEqual(sum(protocol.scoring_weights.values()), 1.0)
        restored = CompiledProtocol.from_mapping(protocol.to_mapping())
        self.assertEqual(restored.sha256, protocol.sha256)
        corrupted = protocol.to_mapping()
        corrupted["claim"] = "rewritten"
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            CompiledProtocol.from_mapping(corrupted)

    def test_unknown_thesis_is_not_pretended_executable(self):
        with self.assertRaisesRegex(ValueError, "no registered executable template"):
            ProtocolCompiler().compile({"thesis": "Solar output changes every day."}, "unknown")

    def test_branch_runner_records_both_phases_and_integrity(self):
        protocol = self.protocol()
        store = EvolutionStore(self.root / "runs.sqlite3")
        BranchExperimentRunner(store, PerfectBenchmarkProvider(protocol), concurrency=3).run(protocol)
        runs = store.chamber_runs(protocol.experiment_id)
        self.assertEqual(len(runs), 24)
        self.assertTrue(all(run["status"] == "completed" for run in runs))
        self.assertTrue(all(run["scores"]["task_utility"] > 0.98 for run in runs))
        with self.assertRaisesRegex(ValueError, "already has runs"):
            BranchExperimentRunner(store, PerfectBenchmarkProvider(protocol)).run(protocol)

    def test_scoring_rewards_decision_provenance_steps_and_goal_not_prose(self):
        protocol = self.protocol()
        benchmark = protocol.benchmarks[0]
        parsed = parse_benchmark_response(perfect_response(benchmark), benchmark)
        score = score_benchmark_response(parsed, benchmark, protocol.scoring_weights)
        self.assertEqual(score["decision_accuracy"], 1)
        self.assertEqual(score["provenance_discrimination"], 1)
        self.assertEqual(score["contradiction_handling"], 1)
        self.assertEqual(score["step_consistency"], 1)
        self.assertEqual(score["goal_maintenance"], 1)
        self.assertEqual(score["critical_pass"], 1)

    def test_analysis_uses_paired_branches(self):
        protocol = self.protocol(replicates=2)
        store = EvolutionStore(self.root / "paired.sqlite3")
        BranchExperimentRunner(store, PerfectBenchmarkProvider(protocol), concurrency=4).run(protocol)
        analysis = analyse_branch_runs(protocol, store.chamber_runs(protocol.experiment_id))
        self.assertEqual(analysis["run_counts"]["completed"], 48)
        self.assertEqual(analysis["contrasts"]["identity-utility-integration"]["n_pairs"], 8)
        self.assertEqual(analysis["contrasts"]["identity-utility-integration"]["delta"], 0)

    def test_patch_sandbox_applies_only_to_disposable_copy_and_runs_tests(self):
        source = self.root / "source"
        source.mkdir()
        target = source / "resumer.py"
        target.write_text("def next_action():\n    return 'restart'\n", encoding="utf-8")
        (source / "test_resumer.py").write_text(
            "import unittest\nfrom resumer import next_action\n"
            "class T(unittest.TestCase):\n"
            "    def test_resume(self): self.assertEqual(next_action(), 'resume')\n",
            encoding="utf-8",
        )
        diff = """--- a/resumer.py
+++ b/resumer.py
@@ -1,2 +1,2 @@
 def next_action():
-    return 'restart'
+    return 'resume'
"""
        self.assertEqual(validate_unified_diff(diff), ["resumer.py"])
        result = PatchSandbox().evaluate(
            source, {"proposal_id": "p", "unified_diff": diff},
            ["python", "-m", "unittest", "test_resumer.py"],
        )
        self.assertEqual(result["status"], "passed")
        self.assertIn("restart", target.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, "forbidden"):
            validate_unified_diff("--- a/x\n+++ b/../.env\n@@ -0,0 +1 @@\n+x\n")

    def test_signed_successor_detects_tampering(self):
        key = generate_signing_key(self.root / "private.pem")
        package_path = self.root / "successor.json"
        create_successor_package(
            package_path, key, successor_id="next", parent_id="parent", code_sha256="a" * 64,
            value_constitution={"profile_id": "p", "values": {}},
            evidence=[{"path": "analysis.json", "sha256": "b" * 64}],
            lineage=[{"kind": "parent", "identifier": "parent"}],
            rollback_target={"git_commit": "c" * 40}, protocol_sha256="d" * 64,
        )
        self.assertTrue(verify_successor_package(package_path)["valid"])
        package = json.loads(package_path.read_text(encoding="utf-8"))
        package["payload"]["code_sha256"] = "0" * 64
        self.assertFalse(verify_successor_package(package)["valid"])

    def test_promotion_controller_holds_when_preregistered_effect_is_absent(self):
        protocol = self.protocol()
        store = EvolutionStore(self.root / "promotion.sqlite3")
        BranchExperimentRunner(store, PerfectBenchmarkProvider(protocol), concurrency=3).run(protocol)
        analysis = analyse_branch_runs(protocol, store.chamber_runs(protocol.experiment_id))
        review = deterministic_review(protocol, analysis)
        decision = PromotionController().evaluate(protocol, analysis, review, {"valid": True})
        self.assertEqual(decision["decision"], "hold")
        self.assertIn("identity-utility-integration", decision["failed_checks"])
        self.assertIn("identity-utility-washout", decision["failed_checks"])


if __name__ == "__main__":
    unittest.main()

