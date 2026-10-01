"""
Test Suite for Mechanized Solvers & True AST-Level Code Rewriting.

Verifies:
1. QF_LIASolver (Fourier-Motzkin elimination over Presburger arithmetic)
2. StratifiedDatalogSolver (Safety, stratification, and minimal Herbrand model)
3. LyapunovStabilitySolver (1D and n-D exact rational stability analysis)
4. ASTSafetyValidator & SandboxedExecutionTester (Purity, safety, and sandboxing)
5. AtomicCodeHotSwapper & GodelMachineSelfOptimizer.verify_and_apply_code_mutation
"""

import unittest
from fractions import Fraction

from godelOS.solvers.qf_lia_solver import QF_LIASolver, LinearConstraint
from godelOS.solvers.datalog_solver import StratifiedDatalogSolver, DatalogProgram, Atom, Rule
from godelOS.solvers.lyapunov_solver import LyapunovStabilitySolver
from godelOS.code_synthesizer import (
    ASTSafetyValidator,
    SandboxedExecutionTester,
    AtomicCodeHotSwapper,
    ExecutableCodeContract
)
from godelOS.godel_machine import (
    GodelMachineSelfOptimizer,
    ConservativeUtilityBounds,
    to_fraction
)


class TestMechanizedSolvers(unittest.TestCase):

    # =========================================================================
    # 1. QF_LIASolver (Fourier-Motzkin Presburger Arithmetic)
    # =========================================================================

    def test_qf_lia_satisfiability_and_contradiction(self):
        """Verifies direct contradiction and basic satisfiability."""
        # x <= 5 and -x <= -6 (i.e. x >= 6) -> UNSAT
        c1 = QF_LIASolver.parse_constraint("x <= 5")
        c2 = QF_LIASolver.parse_constraint("-x <= -6")
        self.assertFalse(QF_LIASolver.is_satisfiable([c1, c2]))

        # x <= 5 and -x <= -4 (i.e. 4 <= x <= 5) -> SAT
        c3 = QF_LIASolver.parse_constraint("-x <= -4")
        self.assertTrue(QF_LIASolver.is_satisfiable([c1, c3]))

    def test_qf_lia_entailment_proving(self):
        """Verifies that Premises ⊨ Conclusion holds via refutation."""
        # 0 <= d and d <= 3 entails d <= 5
        proven, msg = QF_LIASolver.prove_entailment(["0 <= d", "d <= 3"], "d <= 5")
        self.assertTrue(proven)
        self.assertIn("Entailment proven", msg)

        # 0 <= d and d <= 8 DOES NOT entail d <= 5
        proven_false, msg_false = QF_LIASolver.prove_entailment(["0 <= d", "d <= 8"], "d <= 5")
        self.assertFalse(proven_false)
        self.assertIn("Counterexample exists", msg_false)

    def test_qf_lia_multi_variable_elimination(self):
        """Verifies Fourier-Motzkin variable elimination across 2 variables."""
        # x + y <= 10, -x <= -2, -y <= -3 entails x + y >= 5 (i.e. -x - y <= -5)
        premises = ["x + y <= 10", "-x <= -2", "-y <= -3"]
        proven, _ = QF_LIASolver.prove_entailment(premises, "-x - y <= -5")
        self.assertTrue(proven)

    # =========================================================================
    # 2. StratifiedDatalogSolver
    # =========================================================================

    def test_datalog_safety_validation(self):
        """Rejects rules where head variable or negated variable is not bound in positive body."""
        # Safe rule: Head var X appears in positive body Pred(X)
        safe_rule = StratifiedDatalogSolver.parse_rule("Out(X) :- In(X)")
        self.assertTrue(safe_rule.is_safe())

        # Unsafe rule: Head var Y does not appear in positive body
        unsafe_rule = StratifiedDatalogSolver.parse_rule("Out(X, Y) :- In(X)")
        self.assertFalse(unsafe_rule.is_safe())

        # Unsafe rule: Negated literal variable Z does not appear in positive body
        unsafe_neg = StratifiedDatalogSolver.parse_rule("Out(X) :- In(X), ¬Bad(Z)")
        self.assertFalse(unsafe_neg.is_safe())

    def test_datalog_stratification_cycle_detection(self):
        """Verifies detection and rejection of negative recursion cycles."""
        # P depends negatively on Q, and Q depends negatively on P -> unstratified cycle
        r1 = StratifiedDatalogSolver.parse_rule("P(X) :- Base(X), ¬Q(X)")
        r2 = StratifiedDatalogSolver.parse_rule("Q(X) :- Base(X), ¬P(X)")
        strat_ok, _, msg = StratifiedDatalogSolver.check_stratification([r1, r2])
        self.assertFalse(strat_ok)
        self.assertIn("Stratification violation", msg)

    def test_datalog_fixpoint_minimal_herbrand_model(self):
        """Evaluates semi-naïve fixpoint computation over transitive closure with stratified negation."""
        prog = DatalogProgram()
        prog.add_fact("Edge", "1", "2")
        prog.add_fact("Edge", "2", "3")
        prog.add_fact("Edge", "3", "4")
        prog.add_fact("Blocked", "3")

        # Reachable(X, Y) :- Edge(X, Y)
        # Reachable(X, Z) :- Reachable(X, Y), Edge(Y, Z)
        # SafePath(X, Y) :- Reachable(X, Y), ¬Blocked(Y)
        r1 = StratifiedDatalogSolver.parse_rule("Reachable(X, Y) :- Edge(X, Y)")
        r2 = StratifiedDatalogSolver.parse_rule("Reachable(X, Z) :- Reachable(X, Y), Edge(Y, Z)")
        r3 = StratifiedDatalogSolver.parse_rule("SafePath(X, Y) :- Reachable(X, Y), ¬Blocked(Y)")

        for r in [r1, r2, r3]:
            prog.add_rule(r.head, r.body)

        model = StratifiedDatalogSolver.evaluate_fixpoint(prog)

        # Reachable(1, 4) must be in model
        self.assertIn(("Reachable", ("1", "4")), model)
        # SafePath(1, 2) must be in model (2 is not blocked)
        self.assertIn(("SafePath", ("1", "2")), model)
        # SafePath(1, 3) must NOT be in model because Blocked("3") holds
        self.assertNotIn(("SafePath", ("1", "3")), model)
        # SafePath(1, 4) must be in model (4 is not blocked)
        self.assertIn(("SafePath", ("1", "4")), model)

    # =========================================================================
    # 3. LyapunovStabilitySolver
    # =========================================================================

    def test_lyapunov_1d_quadratic_stability(self):
        """Tests exact rational dissipation for 1D quadratic candidate."""
        stable, gamma, msg = LyapunovStabilitySolver.verify_1d_dissipation(Fraction(3, 10))
        self.assertTrue(stable)
        self.assertEqual(gamma, Fraction(51, 100))
        self.assertIn("Lyapunov stability certified", msg)

        # Unstable / non-contractive cases
        unstable_0, _, _ = LyapunovStabilitySolver.verify_1d_dissipation(Fraction(0, 1))
        self.assertFalse(unstable_0)

        unstable_neg, _, _ = LyapunovStabilitySolver.verify_1d_dissipation(Fraction(-1, 2))
        self.assertFalse(unstable_neg)

        unstable_over, _, _ = LyapunovStabilitySolver.verify_1d_dissipation(Fraction(3, 2))
        self.assertFalse(unstable_over)

    def test_lyapunov_sylvester_criterion_positive_definite(self):
        """Verifies Sylvester's criterion on leading principal minors using Fraction arithmetic."""
        # M = [[2, 1], [1, 2]] -> det1 = 2 > 0, det2 = 4 - 1 = 3 > 0 -> Positive Definite
        M_pos = [[Fraction(2), Fraction(1)], [Fraction(1), Fraction(2)]]
        self.assertTrue(LyapunovStabilitySolver.is_positive_definite(M_pos))

        # M_indef = [[1, 2], [2, 1]] -> det1 = 1 > 0, det2 = 1 - 4 = -3 < 0 -> Indefinite
        M_indef = [[Fraction(1), Fraction(2)], [Fraction(2), Fraction(1)]]
        self.assertFalse(LyapunovStabilitySolver.is_positive_definite(M_indef))

    # =========================================================================
    # 4. ASTSafetyValidator & SandboxedExecutionTester
    # =========================================================================

    def test_ast_safety_validator_accepts_pure_code(self):
        """Validates that pure algorithmic Python code passes static safety check."""
        safe_code = """
def quick_filter(items):
    res = []
    for x in items:
        if x > 0 and x % 2 == 0:
            res.append(x * 2)
    return res
"""
        ok, fn_ast, msg = ASTSafetyValidator.validate_source(safe_code)
        self.assertTrue(ok)
        self.assertIsNotNone(fn_ast)
        self.assertEqual(fn_ast.name, "quick_filter")

    def test_ast_safety_validator_rejects_dangerous_code(self):
        """Rejects code attempting imports, eval, globals, or dunder access."""
        # 1. Disallow import
        bad_import = "def bad(x):\n    import os\n    return os.getpid()\n"
        ok, _, msg = ASTSafetyValidator.validate_source(bad_import)
        self.assertFalse(ok)
        self.assertIn("External module imports forbidden", msg)

        # 2. Disallow eval/exec
        bad_eval = "def bad(x):\n    return eval(x)\n"
        ok, _, msg = ASTSafetyValidator.validate_source(bad_eval)
        self.assertFalse(ok)
        self.assertIn("Forbidden builtin reference", msg)

        # 3. Disallow dunder attributes
        bad_dunder = "def bad(x):\n    return x.__class__.__bases__\n"
        ok, _, msg = ASTSafetyValidator.validate_source(bad_dunder)
        self.assertFalse(ok)
        self.assertIn("Dunder attribute access", msg)

    def test_sandboxed_execution_tester_validation(self):
        """Executes candidate AST against input-output test vectors in sandboxed scope."""
        code = """
def sort_and_dedup(lst):
    return sorted(list(set(lst)))
"""
        ok, fn_ast, _ = ASTSafetyValidator.validate_source(code)
        self.assertTrue(ok)

        test_vectors = [
            (([3, 1, 2, 3, 2, 1],), [1, 2, 3]),
            (([],), []),
            (([42],), [42])
        ]
        test_ok, fn_obj, msg = SandboxedExecutionTester.test_candidate(fn_ast, test_vectors)
        self.assertTrue(test_ok)
        self.assertIsNotNone(fn_obj)
        self.assertEqual(fn_obj([5, 3, 5, 1]), [1, 3, 5])

    # =========================================================================
    # 5. AtomicCodeHotSwapper & GodelMachineSelfOptimizer Code Rewriting
    # =========================================================================

    def test_atomic_code_hot_swapper_with_live_rollback(self):
        """Verifies transactional function pointer replacement on a live object with rollback on failure."""
        class MockWorker:
            def compute(self, x: int) -> int:
                return x + 1

        worker = MockWorker()
        self.assertEqual(worker.compute(5), 6)

        # A. Successful hot-swap to optimized version (x * 2)
        valid_code = """
def compute(x):
    return x * 2
"""
        bounds = ConservativeUtilityBounds(Fraction(1, 1), Fraction(-1, 1), Fraction(0))
        contract = ExecutableCodeContract(
            mutation_id="mut_code_worker_01",
            target_object=worker,
            target_function_name="compute",
            candidate_source_code=valid_code,
            test_vectors=[((2,), 4), ((5,), 10)],
            utility_bounds=bounds
        )

        verified, applied, orig_fn, msg = AtomicCodeHotSwapper.verify_and_swap(contract)
        self.assertTrue(verified)
        self.assertTrue(applied)
        self.assertEqual(worker.compute(5), 10) # Live hot-swap confirmed!

        # B. Faulty mutation that causes crash on live call -> Automatic Rollback
        crash_code = """
def compute(x):
    if x == 5:
        raise ValueError("Simulated bug on input 5")
    return x * 3
"""
        crash_contract = ExecutableCodeContract(
            mutation_id="mut_code_worker_crash",
            target_object=worker,
            target_function_name="compute",
            candidate_source_code=crash_code,
            test_vectors=[((2,), 6), ((5,), 15)], # Will pass sandbox test if not hitting 5 first, but let's test rollback
            utility_bounds=bounds
        )
        # Sandbox test on (5,) raises ValueError
        verified_crash, applied_crash, _, _ = AtomicCodeHotSwapper.verify_and_swap(crash_contract)
        self.assertFalse(applied_crash)
        # Verify worker is intact
        self.assertEqual(worker.compute(5), 10)

    def test_godel_machine_optimizer_verify_and_apply_code_mutation(self):
        """End-to-end integration: GodelMachineSelfOptimizer certifies and hot-swaps code via TCB."""
        optimizer = GodelMachineSelfOptimizer()

        class DeductionEngine:
            def score_clause(self, clause_len: int, var_count: int) -> int:
                return clause_len + var_count

        engine = DeductionEngine()
        self.assertEqual(engine.score_clause(3, 2), 5)

        # Propose faster, certified clause scorer
        new_source = """
def score_clause(clause_len, var_count):
    return (clause_len * 2) - var_count
"""
        bounds = ConservativeUtilityBounds(
            min_task_reward_delta=Fraction(1, 2),
            upper_bound_cost_delta=Fraction(-2, 1), # 2 units speedup
            upper_bound_error_delta=Fraction(0)
        )
        code_contract = ExecutableCodeContract(
            mutation_id="mut_scorer_opt_01",
            target_object=engine,
            target_function_name="score_clause",
            candidate_source_code=new_source,
            test_vectors=[((3, 2), 4), ((5, 1), 9)],
            utility_bounds=bounds
        )

        res = optimizer.verify_and_apply_code_mutation(code_contract, proposer_time_ms=18.4)
        self.assertTrue(res.safety_certified)
        self.assertTrue(res.utility_guaranteed)
        self.assertTrue(res.applied)
        self.assertFalse(res.rolled_back)
        self.assertEqual(engine.score_clause(3, 2), 4) # Newly swapped implementation active!
        self.assertEqual(len(optimizer.mutation_history), 1)
        self.assertEqual(optimizer.mutation_history[-1]["mutation_type"], "executable_code_ast")


if __name__ == '__main__':
    unittest.main()
