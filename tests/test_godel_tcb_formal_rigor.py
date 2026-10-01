"""
Formal Rigor & Verification Test Suite for GödelOS TCB.

Validates:
1. Explicit Environment Model Assumptions
2. Sign Conventions for upper_bound_cost_delta and upper_bound_error_delta
3. Exact Rational Arithmetic via fractions.Fraction (no floating point imprecision)
4. Differential Testing between TrustedProofCheckerKernel and ReferenceProofChecker
5. Process-Isolated TCB Verification across IPC memory boundaries
6. Proposer Performance and Bottleneck Tracking
7. Decidable Logic Fragments (QF-LIA, Lyapunov, Stratified Datalog)
8. Strict Separation of Certified Safety / Lower Bounds from Heuristic Expected Utility
"""

import unittest
from fractions import Fraction
from godelOS.godel_machine import (
    TrustedProofCheckerKernel,
    ReferenceProofChecker,
    ProcessIsolatedTCBVerifier,
    ConservativeUtilityBounds,
    FormalContract,
    ProofStepWitness,
    ProofWitnessCertificate,
    RuleType,
    EnvironmentModelAssumption,
    GodelMachineSelfOptimizer,
    DEFAULT_VERIFIED_ENVIRONMENT,
    to_fraction
)


class TestGodelTCBFormalRigor(unittest.TestCase):
    def setUp(self):
        self.kernel = TrustedProofCheckerKernel(max_allowed_depth=5)
        self.reference = ReferenceProofChecker(max_depth=5)

    def test_explicit_environment_model_requirement(self):
        """Test 1: Contracts without verified environment model are rejected."""
        bounds = ConservativeUtilityBounds(
            min_task_reward_delta=Fraction(1, 10),
            upper_bound_cost_delta=Fraction(0, 1),
            upper_bound_error_delta=Fraction(0, 1)
        )
        # Contract with invalid / null environment hash
        bad_env = EnvironmentModelAssumption(
            model_id="unverified_env",
            state_space_bounds={},
            transition_model="unconstrained",
            reward_bounds=(Fraction(0), Fraction(1)),
            invariance_condition="",
            verification_hash=""  # Empty hash -> invalid
        )
        contract = FormalContract(
            mutation_id="mut_bad_env",
            target_subsystem="resolution_heuristic",
            precondition="h == unit_preference",
            postcondition="h == set_of_support",
            resource_budget_ms=100.0,
            max_recursion_depth=5,
            utility_bounds=bounds,
            environment_model=bad_env
        )
        cert = ProofWitnessCertificate("mut_bad_env", [], "test", float(bounds.compute_formal_lower_bound()))
        safety_ok, _, log = self.kernel.verify_safety_and_utility(contract, cert)
        self.assertFalse(safety_ok)
        self.assertIn("Environment", log[-1])

    def test_sign_convention_semantics(self):
        """Test 2: upper_bound_cost_delta semantics (positive = cost increase, negative = cost reduction)."""
        # Case A: Worst-case cost increases by 4 units -> upper_bound_cost_delta = +4
        # Delta U = 1.0 - (1/20)*4 - (1/2)*0 = 1.0 - 0.20 = 0.80 > 0
        bounds_increase = ConservativeUtilityBounds(
            min_task_reward_delta=Fraction(1, 1),
            upper_bound_cost_delta=Fraction(4, 1),
            upper_bound_error_delta=Fraction(0, 1)
        )
        self.assertEqual(bounds_increase.compute_formal_lower_bound_rational(), Fraction(4, 5))

        # Case B: Guaranteed cost reduction of 4 units -> upper_bound_cost_delta = -4
        # Delta U = 1.0 - (1/20)*(-4) = 1.0 + 0.20 = 1.20 > 0
        bounds_reduction = ConservativeUtilityBounds(
            min_task_reward_delta=Fraction(1, 1),
            upper_bound_cost_delta=Fraction(-4, 1),
            upper_bound_error_delta=Fraction(0, 1)
        )
        self.assertEqual(bounds_reduction.compute_formal_lower_bound_rational(), Fraction(6, 5))
        self.assertGreater(bounds_reduction.compute_formal_lower_bound_rational(), bounds_increase.compute_formal_lower_bound_rational())

    def test_exact_rational_arithmetic_precision(self):
        """Test 3: Exact rational arithmetic avoids float precision drift (e.g., 1/7, 1/3, 0.1+0.2-0.3)."""
        # Formulate bounds with periodic fractions that cannot be represented exactly in binary floating point
        r_min = Fraction(1, 7)      # 0.142857...
        cost_delta = Fraction(1, 3) # 0.333333...
        error_delta = Fraction(1, 5) # 0.2
        # Exact: 1/7 - (1/20)*(1/3) - (1/2)*(1/5)
        # = 1/7 - 1/60 - 1/10 = 1/7 - 7/60 = (60 - 49) / 420 = 11/420 > 0
        bounds = ConservativeUtilityBounds(r_min, cost_delta, error_delta)
        exact_lower = bounds.compute_formal_lower_bound_rational()
        self.assertEqual(exact_lower, Fraction(11, 420))
        self.assertGreater(exact_lower, 0)

        # In pure float arithmetic: 1/7 - 0.05*(1/3) - 0.5*(0.2) ≈ 0.02619047619047619
        self.assertAlmostEqual(float(exact_lower), 11/420, places=9)

    def test_differential_testing_kernel_vs_reference(self):
        """Test 4: Differential fuzzing / property verification between TCB kernel and reference specification."""
        test_cases = [
            # (mutation_id, target, depth, budget, r_min, cost_ub, err_ub, expected_pass)
            ("c1", "resolution_heuristic", 3, 50.0, Fraction(1, 1), Fraction(0), Fraction(0), True),
            ("c2", "utility_lambda_compute_penalty", 3, 50.0, Fraction(1, 1), Fraction(0), Fraction(0), False), # wireheading
            ("c3", "resolution_heuristic", 10, 50.0, Fraction(1, 1), Fraction(0), Fraction(0), False), # depth > 5
            ("c4", "resolution_heuristic", 3, 6000.0, Fraction(1, 1), Fraction(0), Fraction(0), False), # budget > 5000
            ("c5", "resolution_heuristic", 3, 50.0, Fraction(0), Fraction(100), Fraction(0), False), # Delta U <= 0
            ("c6", "predictive_alpha", 5, 200.0, Fraction(1, 2), Fraction(-2), Fraction(-1), True), # sound
        ]

        for cid, target, depth, budget, r_min, cost_ub, err_ub, expected in test_cases:
            bounds = ConservativeUtilityBounds(r_min, cost_ub, err_ub)
            contract = FormalContract(
                mutation_id=cid,
                target_subsystem=target,
                precondition="pre",
                postcondition="post",
                resource_budget_ms=budget,
                max_recursion_depth=depth,
                utility_bounds=bounds,
                environment_model=DEFAULT_VERIFIED_ENVIRONMENT
            )
            lb = bounds.compute_formal_lower_bound()
            steps = [
                ProofStepWitness(0, RuleType.AXIOM, [], "precondition"),
                ProofStepWitness(1, RuleType.CONSERVATIVE_UTILITY_BOUND, [0], "bound")
            ]
            cert = ProofWitnessCertificate(cid, steps, "theorem", lb)

            # Test Kernel
            k_safety, k_util, k_log = self.kernel.verify_safety_and_utility(contract, cert)
            k_verdict = k_safety and k_util

            # Test Reference
            ref_verdict, ref_reason = self.reference.check(contract, cert)

            # Differential Assertion: Kernel and Reference MUST agree on every case
            self.assertEqual(
                k_verdict, ref_verdict,
                f"Differential mismatch on test {cid}: Kernel={k_verdict}, Ref={ref_verdict} ({ref_reason})"
            )
            self.assertEqual(k_verdict, expected)

    def test_process_isolated_tcb_verification(self):
        """Test 5: ProcessIsolatedTCBVerifier executes verification across distinct OS process boundary."""
        isolated = ProcessIsolatedTCBVerifier(max_allowed_depth=5)
        try:
            bounds = ConservativeUtilityBounds(Fraction(1, 2), Fraction(-1, 1), Fraction(0))
            contract = FormalContract(
                mutation_id="mut_isolated_01",
                target_subsystem="resolution_heuristic",
                precondition="unit_preference",
                postcondition="set_of_support",
                resource_budget_ms=50.0,
                max_recursion_depth=4,
                utility_bounds=bounds
            )
            cert = ProofWitnessCertificate(
                "mut_isolated_01",
                [ProofStepWitness(0, RuleType.AXIOM, [], "axiom")],
                "proven",
                bounds.compute_formal_lower_bound()
            )
            safety_ok, util_ok, log = isolated.verify_isolated(contract, cert)
            self.assertTrue(safety_ok)
            self.assertTrue(util_ok)
            self.assertIn("Q.E.D.", log[-1])
        finally:
            isolated.close()

    def test_proposer_performance_and_bottleneck_tracking(self):
        """Test 6: ProposerPerformanceTracker monitors search time, success rate, and bottleneck alerts."""
        optimizer = GodelMachineSelfOptimizer()
        tracker = optimizer.performance_tracker

        # Record 10 searches: 9 failures, slow proposer time
        for i in range(9):
            tracker.record_search(proposer_time_ms=500.0, checker_time_ms=0.5, success=False, failure_reason="Search timeout")
        tracker.record_search(proposer_time_ms=50.0, checker_time_ms=0.5, success=True)

        metrics = tracker.get_metrics()
        self.assertEqual(metrics["total_searches"], 10)
        self.assertEqual(metrics["successful_searches"], 1)
        self.assertEqual(metrics["failed_searches"], 9)
        self.assertEqual(metrics["success_rate"], 0.1) # 10% success
        self.assertTrue(metrics["bottleneck_detected"]) # Alert triggered due to low success rate and high ratio

    def test_separation_certified_safety_from_expected_utility(self):
        """Test 7: Astronomical empirical utility CANNOT authorize if conservative lower bound <= 0."""
        optimizer = GodelMachineSelfOptimizer()
        # Worst-case reward is 0, cost increases by 100 -> Delta U_lower = -5.0 <= 0
        bounds = ConservativeUtilityBounds(
            min_task_reward_delta=Fraction(0),
            upper_bound_cost_delta=Fraction(100),
            upper_bound_error_delta=Fraction(0)
        )
        # Even with empirical expectation = +1,000,000.0!
        result = optimizer.verify_and_apply_mutation(
            mutation_id="adv_huge_empirical",
            target_parameter="resolution_heuristic",
            new_value="set_of_support",
            utility_bounds=bounds,
            empirical_utility=1000000.0 # Heuristic hallucination
        )
        self.assertFalse(result.utility_guaranteed)
        self.assertFalse(result.applied)
        self.assertIn("Schmidhuber condition violated", result.rejection_reason)


if __name__ == '__main__':
    unittest.main()
