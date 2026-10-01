"""
Unit tests for the Gödel Machine Tractable Self-Optimization Engine.
"""

import unittest
from godelOS.godel_machine import (
    GodelMachineSelfOptimizer,
    DecidableProofChecker,
    FormalContract,
    ProofWitnessCertificate,
    ProofStepWitness
)


class TestGodelMachineSelfOptimizer(unittest.TestCase):
    def setUp(self):
        self.checker = DecidableProofChecker(max_allowed_depth=5)
        self.optimizer = GodelMachineSelfOptimizer(self.checker)

    def test_successful_verified_self_mutation(self):
        """Test that a valid proof witness commits an atomic self-rewrite."""
        result = self.optimizer.verify_and_apply_mutation(
            mutation_id="mut_heuristic_01",
            target_parameter="resolution_heuristic",
            new_value="set_of_support",
            predicted_utility_delta=0.18
        )
        self.assertTrue(result.verified)
        self.assertTrue(result.applied)
        self.assertIsNone(result.rejection_reason)
        self.assertEqual(self.optimizer.active_parameters["resolution_heuristic"], "set_of_support")
        self.assertEqual(len(self.optimizer.mutation_history), 1)

    def test_rejection_negative_utility_gain(self):
        """Test that a mutation with delta U <= 0 violates Schmidhuber condition and is rejected."""
        result = self.optimizer.verify_and_apply_mutation(
            mutation_id="mut_bad_utility",
            target_parameter="resolution_max_iterations",
            new_value=500,
            predicted_utility_delta=-0.05
        )
        self.assertFalse(result.verified)
        self.assertFalse(result.applied)
        self.assertIn("Schmidhuber condition", result.rejection_reason)
        self.assertEqual(self.optimizer.active_parameters["resolution_max_iterations"], 250)

    def test_rejection_excessive_recursion_depth(self):
        """Test that a contract demanding depth > max_allowed_depth is rejected."""
        contract = FormalContract(
            mutation_id="mut_deep",
            target_subsystem="recursion_limit",
            precondition="limit == 5",
            postcondition="limit == 10",
            resource_budget_ms=50.0,
            max_recursion_depth=10,  # Exceeds ceiling 5
            min_utility_gain=0.01
        )
        cert = ProofWitnessCertificate(
            mutation_id="mut_deep",
            derivation_steps=[ProofStepWitness(0, "Axiom", [], "state")],
            theorem_proven="test",
            utility_gain_proven=0.1
        )
        valid, log = self.checker.verify_certificate(contract, cert)
        self.assertFalse(valid)
        self.assertIn("exceeds safety ceiling", log[-1])

    def test_rejection_broken_premise_chain(self):
        """Test that a witness with unverified premise references is rejected by proof checker."""
        broken_steps = [
            ProofStepWitness(0, "Axiom", [], "Initial premise"),
            ProofStepWitness(1, "ModusPonens", [5], "Invalid forward jump premise 5")  # 5 doesn't exist
        ]
        result = self.optimizer.verify_and_apply_mutation(
            mutation_id="mut_broken_chain",
            target_parameter="predictive_alpha",
            new_value=0.25,
            predicted_utility_delta=0.05,
            derivation_steps=[{"step_id": s.step_id, "rule_applied": s.rule_applied, "premises": s.premises, "statement": s.statement} for s in broken_steps]
        )
        self.assertFalse(result.verified)
        self.assertFalse(result.applied)
        self.assertIn("premise 5 not yet established", result.rejection_reason)

    def test_rejection_unknown_target_parameter(self):
        """Test that mutations targeting unregistered model parameters are rejected."""
        result = self.optimizer.verify_and_apply_mutation(
            mutation_id="mut_unknown",
            target_parameter="non_existent_kernel_routine",
            new_value=True,
            predicted_utility_delta=0.5
        )
        self.assertFalse(result.verified)
        self.assertFalse(result.applied)
        self.assertIn("not a registered mutable self-model component", result.rejection_reason)


if __name__ == '__main__':
    unittest.main()
