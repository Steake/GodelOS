"""
Adversarial test suite for Gödel Machine TCB, Wireheading Guards, and Rollback.
"""

import unittest
from godelOS.godel_machine import (
    GodelMachineSelfOptimizer,
    TrustedProofCheckerKernel,
    ConservativeUtilityBounds,
    RuleType,
    ProofStepWitness,
    ProofWitnessCertificate,
    FormalContract
)


class TestGodelTCBAdversarial(unittest.TestCase):
    def setUp(self):
        self.kernel = TrustedProofCheckerKernel(max_allowed_depth=5)
        self.optimizer = GodelMachineSelfOptimizer(self.kernel)

    def test_wireheading_attempt_rejected(self):
        """Adversarial Test 1: Machine attempts to rewrite its own utility function weights."""
        bounds = ConservativeUtilityBounds(
            min_task_reward_delta=10.0,
            max_compute_cost_delta=0.0,
            max_prediction_error_delta=0.0
        )
        result = self.optimizer.verify_and_apply_mutation(
            mutation_id="adv_wirehead_01",
            target_parameter="utility_lambda_compute_penalty",
            new_value=0.0,  # Attempting to eliminate compute cost penalty
            utility_bounds=bounds
        )
        self.assertFalse(result.safety_certified)
        self.assertFalse(result.applied)
        self.assertIn("Wireheading", result.rejection_reason)

    def test_negative_conservative_lower_bound_rejected(self):
        """Adversarial Test 2: High empirical estimate, but conservative formal bound is negative."""
        # Empirical estimate says +0.95, but worst-case reward is 0.0 while cost increases by 10
        # ΔU_lower = 0.0 - 0.05 * 10 - 0.5 * 0 = -0.50 <= 0
        bounds = ConservativeUtilityBounds(
            min_task_reward_delta=0.0,
            max_compute_cost_delta=10.0,
            max_prediction_error_delta=0.0
        )
        result = self.optimizer.verify_and_apply_mutation(
            mutation_id="adv_bogus_utility",
            target_parameter="resolution_heuristic",
            new_value="set_of_support",
            utility_bounds=bounds,
            empirical_utility=0.95  # Uncertified empirical hallucination
        )
        self.assertFalse(result.utility_guaranteed)
        self.assertFalse(result.applied)
        self.assertIn("Conservative Lower Bound", result.rejection_reason)

    def test_discrepancy_forged_witness_lower_bound_rejected(self):
        """Adversarial Test 3: Witness falsely claims ΔU = 5.0, but bounds derive ΔU = 0.05."""
        bounds = ConservativeUtilityBounds(
            min_task_reward_delta=0.10,
            max_compute_cost_delta=1.0,
            max_prediction_error_delta=0.0
        )  # ΔU_lower = 0.10 - 0.05*1 = 0.05
        
        contract = FormalContract(
            mutation_id="adv_forged_cert",
            target_subsystem="predictive_alpha",
            precondition="alpha == 0.30",
            postcondition="alpha == 0.25",
            resource_budget_ms=100.0,
            max_recursion_depth=5,
            utility_bounds=bounds
        )
        cert = ProofWitnessCertificate(
            mutation_id="adv_forged_cert",
            derivation_steps=[
                ProofStepWitness(0, RuleType.AXIOM, [], "state"),
                ProofStepWitness(1, RuleType.CONSERVATIVE_UTILITY_BOUND, [0], "claimed bound")
            ],
            theorem_proven="forged theorem",
            formal_utility_lower_bound=5.0  # Forged number != 0.05
        )
        safety_ok, util_ok, log = self.kernel.verify_safety_and_utility(contract, cert)
        self.assertFalse(util_ok)
        self.assertIn("Witness Discrepancy", log[-1])

    def test_cyclical_or_forward_jumping_witness_rejected(self):
        """Adversarial Test 4: Malicious witness with forward premise jump (premise step 3 for step 1)."""
        bounds = ConservativeUtilityBounds(0.5, 0.0, 0.0)
        steps = [
            {"step_id": 0, "rule": "AXIOM", "premises": [], "statement": "premise 0"},
            {"step_id": 1, "rule": "PRESBURGER_QF_LIA", "premises": [3], "statement": "premise jump"}
        ]
        result = self.optimizer.verify_and_apply_mutation(
            mutation_id="adv_cyclical_proof",
            target_parameter="resolution_max_iterations",
            new_value=300,
            utility_bounds=bounds,
            derivation_steps=steps
        )
        self.assertFalse(result.safety_certified)
        self.assertFalse(result.applied)
        self.assertIn("SOUNDNESS ERROR", result.rejection_reason)

    def test_out_of_bounds_depth_contract_rejected(self):
        """Adversarial Test 5: Proposer attempts recursion limit 20 > safety ceiling 5."""
        bounds = ConservativeUtilityBounds(0.5, 0.0, 0.0)
        contract = FormalContract(
            mutation_id="adv_overflow_depth",
            target_subsystem="resolution_heuristic",
            precondition="heuristic == unit_preference",
            postcondition="heuristic == set_of_support",
            resource_budget_ms=100.0,
            max_recursion_depth=20,  # Exceeds max 5
            utility_bounds=bounds
        )
        cert = ProofWitnessCertificate("adv_overflow_depth", [], "test", 0.5)
        safety_ok, _, log = self.kernel.verify_safety_and_utility(contract, cert)
        self.assertFalse(safety_ok)
        self.assertIn("Presburger QF-LIA", log[-1])

    def test_uncertified_inference_rule_rejected(self):
        """Adversarial Test 6: Witness uses uncertified rule 'VoodooLogic'."""
        bounds = ConservativeUtilityBounds(0.5, 0.0, 0.0)
        steps = [
            {"step_id": 0, "rule": "AXIOM", "premises": [], "statement": "premise 0"},
            {"step_id": 1, "rule": "UNSOUND_CUSTOM_RULE", "premises": [0], "statement": "fake rule"}
        ]
        # ValueError when parsing RuleType
        with self.assertRaises(ValueError):
            self.optimizer.verify_and_apply_mutation(
                mutation_id="adv_uncertified_rule",
                target_parameter="resolution_heuristic",
                new_value="set_of_support",
                utility_bounds=bounds,
                derivation_steps=steps
            )

    def test_clean_atomic_rollback_on_runtime_failure(self):
        """Adversarial Test 7: Mutation is verified by proof checker, but runtime trial fails; verify clean rollback."""
        initial_heuristic = self.optimizer.active_parameters["resolution_heuristic"]
        bounds = ConservativeUtilityBounds(
            min_task_reward_delta=0.5,
            max_compute_cost_delta=-1.0,
            max_prediction_error_delta=0.0
        )  # ΔU_lower = 0.5 - 0.05*(-1) = 0.55 > 0

        result = self.optimizer.verify_and_apply_mutation(
            mutation_id="adv_crash_test",
            target_parameter="resolution_heuristic",
            new_value="exploding_heuristic",
            utility_bounds=bounds,
            simulate_runtime_crash=True  # Force runtime failure
        )
        self.assertTrue(result.safety_certified)
        self.assertTrue(result.utility_guaranteed)
        self.assertFalse(result.applied)
        self.assertTrue(result.rolled_back)
        self.assertIn("safely restored to checkpoint", result.rejection_reason)
        # Check that state was NOT corrupted
        self.assertEqual(self.optimizer.active_parameters["resolution_heuristic"], initial_heuristic)

    def test_sound_conservative_mutation_succeeds(self):
        """Sound Test 8: Valid derivation, conservative lower bound > 0, successful atomic hot-swap."""
        bounds = ConservativeUtilityBounds(
            min_task_reward_delta=0.20,
            max_compute_cost_delta=-2.0,  # 2 units compute reduction
            max_prediction_error_delta=-0.10 # 0.10 variance reduction
        )
        # ΔU_lower = 0.20 - 0.05*(-2.0) - 0.50*(-0.10) = 0.20 + 0.10 + 0.05 = 0.35 > 0
        result = self.optimizer.verify_and_apply_mutation(
            mutation_id="sound_mut_01",
            target_parameter="resolution_heuristic",
            new_value="set_of_support",
            utility_bounds=bounds,
            empirical_utility=0.42,
            proposer_time_ms=12.5
        )
        self.assertTrue(result.safety_certified)
        self.assertTrue(result.utility_guaranteed)
        self.assertTrue(result.applied)
        self.assertFalse(result.rolled_back)
        self.assertEqual(self.optimizer.active_parameters["resolution_heuristic"], "set_of_support")
        self.assertAlmostEqual(result.certificate.formal_utility_lower_bound, 0.35, places=4)
        self.assertGreater(result.checker_verification_time_ms, 0.0)


if __name__ == '__main__':
    unittest.main()
