"""
Tests for Formal System Verification & Invariant Proofs.
"""

import unittest
from godelOS.formal_verification import FormalSystemVerifier
from godelOS.core_kr.ast.nodes import ConstantNode, ConnectiveNode
from godelOS.core_kr.type_system.types import AtomicType


class TestFormalSystemVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = FormalSystemVerifier(max_recursion_depth=5)
        self.bool_type = AtomicType("Boolean")

    def test_bounded_recursion_valid(self):
        res = self.verifier.verify_bounded_recursion(current_depth=3)
        self.assertTrue(res.proven)
        self.assertEqual(res.invariant_name, "BoundedRecursionDepth")

    def test_bounded_recursion_violation(self):
        res = self.verifier.verify_bounded_recursion(current_depth=8)
        self.assertFalse(res.proven)

    def test_error_contraction_valid(self):
        errors = [0.5, 0.4, 0.35, 0.28, 0.22]
        res = self.verifier.verify_error_contraction(errors, alpha=0.3)
        self.assertTrue(res.proven)
        self.assertIn("Banach fixed-point", res.proof_steps[-1])

    def test_error_contraction_invalid_alpha(self):
        errors = [0.5, 0.4]
        res = self.verifier.verify_error_contraction(errors, alpha=0.0)
        self.assertFalse(res.proven)

    def test_non_contradiction_consistent(self):
        p_atom = ConstantNode("P", self.bool_type)
        q_atom = ConstantNode("Q", self.bool_type)
        res = self.verifier.verify_non_contradiction(axioms=[p_atom], hypothesis=q_atom)
        self.assertTrue(res.proven)

    def test_non_contradiction_inconsistent(self):
        p_atom = ConstantNode("P", self.bool_type)
        not_p = ConnectiveNode("NOT", [p_atom], self.bool_type)
        # Axiom P and hypothesis ¬P should be inconsistent
        res = self.verifier.verify_non_contradiction(axioms=[p_atom], hypothesis=not_p)
        self.assertFalse(res.proven)

    def test_comprehensive_verification(self):
        summary = self.verifier.run_comprehensive_system_verification(current_depth=2)
        self.assertTrue(summary["all_invariants_proven"])
        self.assertEqual(summary["verification_status"], "VERIFIED")
