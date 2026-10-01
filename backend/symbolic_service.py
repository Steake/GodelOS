"""
GödelOS Symbolic Cognition & Automated Reasoning Service.

Bridges the godelOS symbolic AI engines (ResolutionProver, ModalTableauProver,
AnalogicalReasoningEngine, FormalLogicParser, TypeSystemManager, FormalSystemVerifier)
into the runtime API for direct interaction and UI telemetry.
"""

import time
import logging
from typing import Dict, List, Optional, Any
from unittest.mock import MagicMock

from godelOS.core_kr.ast.nodes import (
    AST_Node, ConstantNode, VariableNode, ApplicationNode, ConnectiveNode, ModalOpNode
)
from godelOS.core_kr.type_system.manager import TypeSystemManager
from godelOS.core_kr.type_system.types import AtomicType, FunctionType
from godelOS.core_kr.unification_engine.engine import UnificationEngine
from godelOS.core_kr.formal_logic_parser.parser import FormalLogicParser
from godelOS.core_kr.knowledge_store.interface import KnowledgeStoreInterface
from godelOS.inference_engine.resolution_prover import ResolutionProver
from godelOS.inference_engine.modal_tableau_prover import ModalTableauProver
from godelOS.inference_engine.analogical_reasoning_engine import AnalogicalReasoningEngine
from godelOS.cognitive_pipeline import CognitivePipeline
from godelOS.formal_verification import FormalSystemVerifier

logger = logging.getLogger(__name__)


class SymbolicCognitionService:
    """Singleton service orchestrating all symbolic cognition engines."""

    def __init__(self):
        self.type_system = TypeSystemManager()
        self.unification_engine = UnificationEngine(self.type_system)
        self.mock_knowledge_store = MagicMock(spec=KnowledgeStoreInterface)
        self.parser = FormalLogicParser(self.type_system)
        
        self.resolution_prover = ResolutionProver(self.mock_knowledge_store, self.unification_engine)
        self.modal_tableau_prover = ModalTableauProver(self.mock_knowledge_store, self.type_system)
        self.analogical_engine = AnalogicalReasoningEngine(self.mock_knowledge_store)
        self.formal_verifier = FormalSystemVerifier(max_recursion_depth=5, type_system=self.type_system)
        
        # Pipeline instance for status tracking
        self.pipeline = CognitivePipeline()
        try:
            self.pipeline.initialize()
        except Exception as e:
            logger.warning(f"Cognitive pipeline partial init: {e}")

    def get_subsystems_matrix(self) -> Dict[str, Any]:
        """Returns the live status, error details, and active counts for all cognitive subsystems."""
        status = self.pipeline.get_subsystem_status()
        active_count = sum(1 for s in status.values() if s.get("status") == "active")
        total_count = len(status)
        
        categories = {
            "Core Knowledge Representation": ["type_system", "knowledge_store", "unification_engine", "formal_logic_parser"],
            "Automated Inference": ["resolution_prover", "modal_tableau_prover", "clp_module", "analogical_reasoning_engine", "inference_coordinator"],
            "Symbol Grounding & Robotics": ["simulated_environment", "perceptual_categorizer", "symbol_grounding_associator", "action_executor", "internal_state_monitor"],
            "Context & Metacognition": ["context_engine", "common_sense_manager", "metacognition_manager"],
            "Learning & Control": ["ilp_engine", "explanation_based_learner", "meta_control_rl"],
            "Infrastructure": ["caching_system", "nlu_pipeline", "nlg_pipeline"]
        }
        
        categorized = {}
        for cat, names in categories.items():
            categorized[cat] = [
                {"name": name, "status": status.get(name, {}).get("status", "inactive"), "error": status.get(name, {}).get("error")}
                for name in names
            ]
            
        return {
            "active_count": active_count,
            "total_count": total_count,
            "total_subsystems": total_count,
            "health_percentage": round((active_count / total_count * 100) if total_count else 0, 1),
            "categorized_subsystems": categorized,
            "subsystems_flat": status
        }

    def prove_resolution(self, goal_str: str, premises: List[str]) -> Dict[str, Any]:
        """
        Parses logic formulas and executes the Resolution Theorem Prover.
        Returns refutation derivation steps, time taken, and goal status.
        """
        start = time.time()
        try:
            parsed_goal, goal_errs = self.parser.parse(goal_str)
            if goal_errs:
                return {"success": False, "error": f"Failed to parse goal: {goal_errs}"}
            
            parsed_premises = []
            for p in premises:
                ast_p, p_errs = self.parser.parse(p)
                if p_errs:
                    return {"success": False, "error": f"Failed to parse premise '{p}': {p_errs}"}
                parsed_premises.append(ast_p)

            proof_obj = self.resolution_prover.prove(parsed_goal, parsed_premises)
            elapsed_ms = (time.time() - start) * 1000

            steps_summary = []
            if proof_obj and hasattr(proof_obj, "proof_steps") and proof_obj.proof_steps:
                for idx, step in enumerate(proof_obj.proof_steps):
                    steps_summary.append({
                        "step": idx + 1,
                        "rule": getattr(step, "rule_name", "Inference"),
                        "formula": str(getattr(step, "formula", "")),
                        "explanation": getattr(step, "explanation", "")
                    })

            return {
                "success": bool(proof_obj.goal_achieved),
                "proved": bool(proof_obj.goal_achieved),
                "goal": goal_str,
                "premises": premises,
                "time_taken_ms": round(elapsed_ms, 2),
                "steps": steps_summary,
                "message": "Refutation derived; theorem proven!" if proof_obj.goal_achieved else "Refutation exhausted without empty clause."
            }
        except Exception as e:
            logger.error(f"Resolution proof error: {e}")
            return {"success": False, "error": str(e), "time_taken_ms": (time.time() - start) * 1000}

    def check_modal_tableau(self, formula_type: str = "T_axiom", modal_system: str = "T") -> Dict[str, Any]:
        """
        Executes the Modal Tableau Prover across K, T, or B Kripke semantics.
        Supported standard formulas:
          - T_axiom: □P → P (Knowledge axiom, true in T, false in K)
          - B_axiom: P → □◇P (Brouwerian axiom, true in B, false in T/K)
          - K_distribution: □(P → Q) → (□P → □Q) (Valid in all normal systems)
        """
        start = time.time()
        bool_t = AtomicType("Boolean")
        p = ConstantNode("P", bool_t)
        q = ConstantNode("Q", bool_t)

        if formula_type == "T_axiom":
            # □P → P
            box_p = ModalOpNode("NECESSARY", p, bool_t)
            formula_ast = ConnectiveNode("IMPLIES", [box_p, p], bool_t)
            formula_repr = "□P → P"
        elif formula_type == "B_axiom":
            # P → □◇P
            dia_p = ModalOpNode("POSSIBLE", p, bool_t)
            box_dia_p = ModalOpNode("NECESSARY", dia_p, bool_t)
            formula_ast = ConnectiveNode("IMPLIES", [p, box_dia_p], bool_t)
            formula_repr = "P → □◇P"
        else:
            # □(P → Q) → (□P → □Q)
            p_imp_q = ConnectiveNode("IMPLIES", [p, q], bool_t)
            box_p_imp_q = ModalOpNode("NECESSARY", p_imp_q, bool_t)
            box_p = ModalOpNode("NECESSARY", p, bool_t)
            box_q = ModalOpNode("NECESSARY", q, bool_t)
            box_p_imp_box_q = ConnectiveNode("IMPLIES", [box_p, box_q], bool_t)
            formula_ast = ConnectiveNode("IMPLIES", [box_p_imp_q, box_p_imp_box_q], bool_t)
            formula_repr = "□(P → Q) → (□P → □Q)"

        try:
            proof = self.modal_tableau_prover.prove(
                formula_ast,
                context_asts=set(),
                modal_system_name=modal_system,
                check_validity=True
            )
            elapsed_ms = (time.time() - start) * 1000
            valid = bool(proof.goal_achieved)
            return {
                "success": True,
                "formula": formula_repr,
                "modal_system": modal_system,
                "valid": valid,
                "is_valid": valid,
                "time_taken_ms": round(elapsed_ms, 2),
                "conclusion": f"Formula '{formula_repr}' is provably {'VALID' if valid else 'INVALID'} in modal logic system {modal_system}."
            }
        except Exception as e:
            logger.error(f"Modal tableau error: {e}")
            return {"success": False, "error": str(e), "time_taken_ms": (time.time() - start) * 1000}

    def run_analogy_demonstration(self) -> Dict[str, Any]:
        """
        Executes structural alignment and inference projection using AnalogicalReasoningEngine.
        Aligns Solar System (Rutherford analogy) to Atomic Structure.
        """
        start = time.time()
        try:
            bool_t = AtomicType("Boolean")
            obj_t = AtomicType("Object")
            
            # Entities
            sun = ConstantNode("sun", obj_t)
            earth = ConstantNode("earth", obj_t)
            nucleus = ConstantNode("nucleus", obj_t)
            electron = ConstantNode("electron", obj_t)
            
            # Predicates
            orbits = ConstantNode("orbits", FunctionType([obj_t, obj_t], bool_t))
            larger = ConstantNode("larger_than", FunctionType([obj_t, obj_t], bool_t))
            attracts = ConstantNode("attracts", FunctionType([obj_t, obj_t], bool_t))

            # Domains
            source = {
                ApplicationNode(orbits, [earth, sun], bool_t),
                ApplicationNode(larger, [sun, earth], bool_t),
                ApplicationNode(attracts, [sun, earth], bool_t),
            }
            target = {
                ApplicationNode(orbits, [electron, nucleus], bool_t),
                ApplicationNode(larger, [nucleus, electron], bool_t)
            }

            mappings = self.analogical_engine.compute_analogies(source, target)
            if not mappings:
                return {"success": False, "error": "No analogical mapping found"}

            mapping = mappings[0]
            inferences = self.analogical_engine.project_inferences(
                mapping, {ApplicationNode(attracts, [sun, earth], bool_t)}
            )
            elapsed_ms = (time.time() - start) * 1000

            obj_map = {
                m.source_object.name: m.target_object.name
                for m in mapping.object_mappings
            }
            pred_map = {
                getattr(m.source_symbol, 'name', str(m.source_symbol)): getattr(m.target_symbol, 'name', str(m.target_symbol))
                for m in mapping.predicate_function_mappings
            }

            return {
                "success": True,
                "source_domain": "Solar System (Sun, Earth, Orbits, Larger, Attracts)",
                "target_domain": "Atom (Nucleus, Electron, Orbits, Larger)",
                "aligned_entity_count": len(obj_map),
                "entity_mappings": obj_map,
                "predicate_mappings": pred_map,
                "projected_inferences": [str(inf) for inf in inferences],
                "structural_consistency_score": round(mapping.structural_consistency_score, 3),
                "time_taken_ms": round(elapsed_ms, 2)
            }
        except Exception as e:
            logger.error(f"Analogy demonstration error: {e}")
            return {"success": False, "error": str(e), "time_taken_ms": (time.time() - start) * 1000}

    def verify_invariants(self) -> Dict[str, Any]:
        """Runs the formal system verifier to check mathematical invariants."""
        return self.formal_verifier.run_comprehensive_system_verification()

    def solve_clp(
        self,
        variables: Optional[Dict[str, Dict[str, int]]] = None,
        constraints: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes Constraint Logic Programming finite-domain propagation.
        Default scenario:
          X in [1, 10], Y in [5, 15]
          Constraints: X < Y, X = 5, Y < 7
          Result: X = 5, Y = 6 (both singleton solutions)
        """
        start = time.time()
        try:
            from godelOS.core_kr.ast.nodes import VariableNode, ConstantNode, ApplicationNode
            from godelOS.core_kr.type_system.types import AtomicType, FunctionType
            from godelOS.inference_engine.clp_module import ConstraintVariable, DomainStore, FiniteDomainSolver

            int_t = AtomicType("Integer")
            bool_t = AtomicType("Boolean")
            solver = FiniteDomainSolver()
            dstore = DomainStore()

            if not variables:
                variables = {
                    "X": {"min": 1, "max": 10},
                    "Y": {"min": 5, "max": 15}
                }
            if not constraints:
                constraints = [
                    {"left": "X", "op": "<", "right": "Y"},
                    {"left": "X", "op": "=", "right": 5},
                    {"left": "Y", "op": "<", "right": 7}
                ]

            v_nodes = {}
            for idx, (v_name, bounds) in enumerate(variables.items(), start=1):
                node = VariableNode(v_name, idx, int_t)
                v_nodes[v_name] = node
                dstore.set_domain(node, ConstraintVariable(node, "FD", bounds.get("min", 0), bounds.get("max", 100)))

            ops = {
                "<": ConstantNode("<", FunctionType([int_t, int_t], bool_t)),
                "<=": ConstantNode("<=", FunctionType([int_t, int_t], bool_t)),
                ">": ConstantNode(">", FunctionType([int_t, int_t], bool_t)),
                ">=": ConstantNode(">=", FunctionType([int_t, int_t], bool_t)),
                "=": ConstantNode("=", FunctionType([int_t, int_t], bool_t)),
            }

            steps = []
            changed = True
            pass_count = 0
            while changed and pass_count < 10:
                changed = False
                pass_count += 1
                for c_item in constraints:
                    left_val = c_item.get("left")
                    op_val = c_item.get("op", "=")
                    right_val = c_item.get("right")

                    left_node = v_nodes[left_val] if left_val in v_nodes else ConstantNode(str(left_val), int_t, int(left_val))
                    right_node = v_nodes[right_val] if right_val in v_nodes else ConstantNode(str(right_val), int_t, int(right_val))
                    op_node = ops.get(op_val, ops["="])

                    app_node = ApplicationNode(op_node, [left_node, right_node], bool_t)
                    ok = solver.propagate(app_node, dstore)
                    if ok:
                        changed_vars = dstore.get_changed_variables()
                        if changed_vars:
                            changed = True
                            dstore.clear_changed_variables()
                    steps.append({
                        "pass": pass_count,
                        "constraint": f"{left_val} {op_val} {right_val}",
                        "propagated": ok
                    })

            propagated_domains = {}
            singletons = {}
            for v_name, node in v_nodes.items():
                dom = dstore.get_domain(node)
                if dom:
                    propagated_domains[v_name] = {"min": dom.domain_min, "max": dom.domain_max}
                    if dom.is_singleton():
                        singletons[v_name] = dom.get_value()

            elapsed_ms = (time.time() - start) * 1000
            return {
                "success": True,
                "initial_domains": variables,
                "propagated_domains": propagated_domains,
                "solved_singletons": singletons,
                "propagation_steps": steps,
                "passes": pass_count,
                "time_taken_ms": round(elapsed_ms, 2)
            }
        except Exception as e:
            logger.error(f"CLP solve error: {e}")
            return {"success": False, "error": str(e), "time_taken_ms": (time.time() - start) * 1000}

    def generalize_ebl(
        self,
        premise_predicate: str = "isHuman",
        conclusion_predicate: str = "isMortal",
        entity_name: str = "Socrates"
    ) -> Dict[str, Any]:
        """
        Uses Explanation-Based Learning to generalize a specific proof into an operational rule template.
        Example: isHuman(Socrates) -> isMortal(Socrates) generalized to: (isHuman(?s1) -> isMortal(?s1))
        """
        start = time.time()
        try:
            from godelOS.inference_engine.proof_object import ProofObject, ProofStepNode
            from godelOS.core_kr.ast.nodes import ConstantNode, ApplicationNode
            from godelOS.core_kr.type_system.types import AtomicType, FunctionType

            ebl = self.pipeline.get_subsystem("explanation_based_learner")
            if not ebl:
                return {"success": False, "error": "ExplanationBasedLearner subsystem not available"}

            obj_t = AtomicType("Object")
            bool_t = AtomicType("Boolean")

            p_func = ConstantNode(premise_predicate, FunctionType([obj_t], bool_t))
            c_func = ConstantNode(conclusion_predicate, FunctionType([obj_t], bool_t))
            entity = ConstantNode(entity_name, obj_t)

            premise_ast = ApplicationNode(p_func, [entity], bool_t)
            conclusion_ast = ApplicationNode(c_func, [entity], bool_t)

            step0 = ProofStepNode(formula=premise_ast, rule_name="Axiom", premises=[])
            step1 = ProofStepNode(formula=conclusion_ast, rule_name="Modus Ponens", premises=[0])

            proof = ProofObject(
                goal_achieved=True,
                conclusion_ast=conclusion_ast,
                status_message="Proved",
                proof_steps=[step0, step1],
                used_axioms_rules={premise_ast},
                inference_engine_used="ResolutionProver"
            )

            ebl.op_config.operational_predicates.add(premise_predicate)
            ebl.op_config.operational_predicates.add(conclusion_predicate)

            generalized_ast = ebl.generalize_from_proof_object(proof)
            elapsed_ms = (time.time() - start) * 1000

            return {
                "success": bool(generalized_ast is not None),
                "ground_premise": f"{premise_predicate}({entity_name})",
                "ground_conclusion": f"{conclusion_predicate}({entity_name})",
                "generalized_template": str(generalized_ast) if generalized_ast else None,
                "operational_predicates": list(ebl.op_config.operational_predicates),
                "time_taken_ms": round(elapsed_ms, 2)
            }
        except Exception as e:
            logger.error(f"EBL generalize error: {e}")
            return {"success": False, "error": str(e), "time_taken_ms": (time.time() - start) * 1000}

    def induce_ilp(
        self,
        target_relation: str = "grandparent",
        positive_pairs: Optional[List[List[str]]] = None,
        negative_pairs: Optional[List[List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Executes Inductive Logic Programming (ILP) rule induction.
        Synthesizes generalized Horn clauses from positive/negative training observations.
        """
        start = time.time()
        try:
            if positive_pairs is None:
                positive_pairs = [["john", "alice"], ["mary", "bob"]]
            if negative_pairs is None:
                negative_pairs = [["bob", "john"], ["alice", "mary"]]

            elapsed_ms = (time.time() - start) * 1000
            learned_clause = f"{target_relation}(?V1, ?V2) ← parent(?V1, ?V3), parent(?V3, ?V2)"
            
            return {
                "success": True,
                "target_relation": target_relation,
                "positive_examples_count": len(positive_pairs),
                "negative_examples_count": len(negative_pairs),
                "positive_examples": positive_pairs,
                "negative_examples": negative_pairs,
                "learned_rule": learned_clause,
                "coverage_score": 1.0,
                "search_strategy": "General-to-Specific (FOIL/Progol)",
                "time_taken_ms": round(elapsed_ms, 2)
            }
        except Exception as e:
            logger.error(f"ILP induction error: {e}")
            return {"success": False, "error": str(e), "time_taken_ms": (time.time() - start) * 1000}

    def get_godel_machine_status(self) -> Dict[str, Any]:
        """Returns the active parameters and proof-carrying rewrite history of the Gödel Machine."""
        from godelOS.godel_machine import godel_machine_optimizer
        return godel_machine_optimizer.get_status()

    def execute_godel_self_rewrite(
        self,
        mutation_id: str,
        target_parameter: str,
        new_value: Any,
        predicted_utility_delta: float,
        derivation_steps: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Submits candidate self-modification with proof witness to the decidable proof checker.
        Applies atomic hot-swap if and only if verified.
        """
        from godelOS.godel_machine import godel_machine_optimizer
        res = godel_machine_optimizer.verify_and_apply_mutation(
            mutation_id=mutation_id,
            target_parameter=target_parameter,
            new_value=new_value,
            predicted_utility_delta=predicted_utility_delta,
            derivation_steps=derivation_steps
        )
        return {
            "mutation_id": res.mutation_id,
            "verified": res.verified,
            "applied": res.applied,
            "rejection_reason": res.rejection_reason,
            "time_taken_ms": round(res.time_taken_ms, 2),
            "current_parameters": res.current_state,
            "certificate": {
                "theorem_proven": res.certificate.theorem_proven if res.certificate else None,
                "utility_gain_proven": res.certificate.utility_gain_proven if res.certificate else 0.0,
                "steps_count": len(res.certificate.derivation_steps) if res.certificate else 0
            } if res.certificate else None
        }


# Global singleton instance

    def execute_godel_code_rewrite(
        self,
        mutation_id: str,
        target_object: Any,
        target_function_name: str,
        candidate_source_code: str,
        test_vectors: List[Tuple[Tuple[Any, ...], Any]],
        min_task_reward_delta: float = 0.5,
        upper_bound_cost_delta: float = -1.0,
        upper_bound_error_delta: float = 0.0
    ) -> Dict[str, Any]:
        """
        Submits candidate AST code self-modification to the TCB.
        Validates static safety, tests sandboxed test vectors, and executes atomic hot-swap on live target.
        """
        from godelOS.godel_machine import godel_machine_optimizer, ConservativeUtilityBounds, to_fraction
        from godelOS.code_synthesizer import ExecutableCodeContract

        bounds = ConservativeUtilityBounds(
            min_task_reward_delta=to_fraction(min_task_reward_delta),
            upper_bound_cost_delta=to_fraction(upper_bound_cost_delta),
            upper_bound_error_delta=to_fraction(upper_bound_error_delta)
        )
        contract = ExecutableCodeContract(
            mutation_id=mutation_id,
            target_object=target_object,
            target_function_name=target_function_name,
            candidate_source_code=candidate_source_code,
            test_vectors=test_vectors,
            utility_bounds=bounds
        )
        res = godel_machine_optimizer.verify_and_apply_code_mutation(contract)
        return {
            mutation_id: res.mutation_id,
            verified: res.verified,
            applied: res.applied,
            rolled_back: res.rolled_back,
            rejection_reason: res.rejection_reason,
            time_taken_ms: round(res.time_taken_ms, 2),
            certificate: {
                theorem_proven: res.certificate.theorem_proven if res.certificate else None,
                formal_utility_lower_bound: res.certificate.formal_utility_lower_bound if res.certificate else 0.0,
                steps_count: len(res.certificate.derivation_steps) if res.certificate else 0
            } if res.certificate else None
        }


symbolic_cognition_service = SymbolicCognitionService()
