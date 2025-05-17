"""
Resolution Prover for First-Order Logic and Propositional Logic.

This module implements the ResolutionProver class, which proves goals using the
resolution inference rule, primarily for First-Order Logic (FOL) and propositional logic.
It converts input formulae into Conjunctive Normal Form (CNF) and applies various
resolution strategies to find a refutation.
"""

from typing import Dict, List, Optional, Set, Tuple, Any, FrozenSet
import time
import logging
import copy
from dataclasses import dataclass, field
from enum import Enum

from godelOS.core_kr.ast.nodes import (
    AST_Node, VariableNode, ConstantNode, ConnectiveNode,
    QuantifierNode, ApplicationNode
)
from godelOS.core_kr.unification_engine.engine import UnificationEngine
from godelOS.core_kr.knowledge_store.interface import KnowledgeStoreInterface
from godelOS.inference_engine.base_prover import BaseProver, ResourceLimits
from godelOS.inference_engine.proof_object import ProofObject, ProofStepNode

# Set up logging
logger = logging.getLogger(__name__)


class ResolutionStrategy(Enum):
    """Enumeration of resolution strategies."""
    SET_OF_SUPPORT = "set_of_support"
    UNIT_PREFERENCE = "unit_preference"
    INPUT_RESOLUTION = "input_resolution"
    LINEAR_RESOLUTION = "linear_resolution"


@dataclass(frozen=True)
class Literal:
    """
    Represents a literal in a clause.
    
    A literal is an atomic formula or its negation.
    """
    atom: AST_Node
    is_negated: bool = False
    
    def negate(self) -> 'Literal':
        """Return a new literal with the opposite polarity."""
        return Literal(self.atom, not self.is_negated)
    
    def __str__(self) -> str:
        return f"{'¬' if self.is_negated else ''}{self.atom}"


@dataclass(frozen=True)
class Clause:
    """
    Represents a clause in CNF.
    
    A clause is a disjunction of literals.
    """
    literals: FrozenSet[Literal]
    source: str = "axiom"
    parent_ids: Tuple[int, ...] = field(default_factory=tuple)
    clause_id: int = -1
    
    def __str__(self) -> str:
        if not self.literals:
            return "□"  # Empty clause (contradiction)
        return " ∨ ".join(str(lit) for lit in self.literals)
    
    def is_empty(self) -> bool:
        """Check if this is the empty clause."""
        return len(self.literals) == 0
    
    def is_unit(self) -> bool:
        """Check if this is a unit clause (contains only one literal)."""
        return len(self.literals) == 1


class CNFConverter:
    """
    Converter for transforming logical formulas into Conjunctive Normal Form (CNF).
    
    This class handles the various steps of CNF conversion:
    1. Eliminate implications and equivalences
    2. Move negations inward (using De Morgan's laws)
    3. Standardize variables apart
    4. Skolemize existential quantifiers
    5. Drop universal quantifiers
    6. Distribute disjunctions over conjunctions
    """
    
    def __init__(self, unification_engine: UnificationEngine):
        """
        Initialize the CNF converter.
        
        Args:
            unification_engine: Engine for unifying logical expressions
        """
        self.unification_engine = unification_engine
        self.next_var_id = 10000
        self.next_skolem_id = 0
    
    def convert_to_cnf(self, formula: AST_Node) -> List[Clause]:
        """
        Convert a formula to CNF.
        
        Args:
            formula: The formula to convert
            
        Returns:
            A list of clauses representing the formula in CNF
        """
        logger.info(f"Converting to CNF: {formula}")
        
        # Step 1: Eliminate implications and equivalences
        step1 = self._eliminate_implications(formula)
        logger.debug(f"After eliminating implications: {step1}")
        
        # Step 2: Move negations inward
        step2 = self._move_negations_inward(step1)
        logger.debug(f"After moving negations inward: {step2}")
        
        # Step 3: Standardize variables apart
        step3 = self._standardize_variables(step2)
        logger.debug(f"After standardizing variables: {step3}")
        
        # Step 4: Skolemize existential quantifiers
        step4 = self._skolemize(step3)
        logger.debug(f"After skolemization: {step4}")
        
        # Step 5: Drop universal quantifiers
        step5 = self._drop_quantifiers(step4)
        logger.debug(f"After dropping quantifiers: {step5}")
        
        # Step 6: Convert to CNF
        step6 = self._distribute_or_over_and(step5)
        logger.debug(f"After distributing OR over AND: {step6}")
        
        # Step 7: Extract clauses
        clauses = self._extract_clauses(step6)
        logger.info(f"Extracted {len(clauses)} clauses")
        
        return clauses
    
    def _eliminate_implications(self, formula: AST_Node) -> AST_Node:
        """
        Eliminate implications and equivalences from a formula.
        
        A → B becomes ¬A ∨ B
        A ↔ B becomes (¬A ∨ B) ∧ (A ∨ ¬B)
        
        Args:
            formula: The formula to transform
            
        Returns:
            The transformed formula
        """
        if isinstance(formula, ConnectiveNode):
            if formula.connective_type == "IMPLIES":
                # A → B becomes ¬A ∨ B
                antecedent = formula.operands[0]
                consequent = formula.operands[1]
                
                # Create ¬A
                negated_antecedent = ConnectiveNode(
                    "NOT",
                    [self._eliminate_implications(antecedent)],
                    formula.type
                )
                
                # Create ¬A ∨ B
                return ConnectiveNode(
                    "OR",
                    [negated_antecedent, self._eliminate_implications(consequent)],
                    formula.type
                )
                
            elif formula.connective_type == "EQUIV":
                # A ↔ B becomes (¬A ∨ B) ∧ (A ∨ ¬B)
                left = formula.operands[0]
                right = formula.operands[1]
                
                # Process subformulas recursively
                left_processed = self._eliminate_implications(left)
                right_processed = self._eliminate_implications(right)
                
                # Create ¬A and ¬B
                not_left = ConnectiveNode("NOT", [left_processed], formula.type)
                not_right = ConnectiveNode("NOT", [right_processed], formula.type)
                
                # Create (¬A ∨ B) and (A ∨ ¬B)
                left_to_right = ConnectiveNode("OR", [not_left, right_processed], formula.type)
                right_to_left = ConnectiveNode("OR", [left_processed, not_right], formula.type)
                
                # Create (¬A ∨ B) ∧ (A ∨ ¬B)
                return ConnectiveNode("AND", [left_to_right, right_to_left], formula.type)
                
            else:
                # Process other connectives recursively
                new_operands = [self._eliminate_implications(op) for op in formula.operands]
                return ConnectiveNode(formula.connective_type, new_operands, formula.type)
                
        elif isinstance(formula, QuantifierNode):
            # Process the scope recursively
            new_scope = self._eliminate_implications(formula.scope)
            return QuantifierNode(
                formula.quantifier_type,
                list(formula.bound_variables),
                new_scope,
                formula.type
            )
        
        # For other node types, return as is
        return formula
    
    def _move_negations_inward(self, formula: AST_Node) -> AST_Node:
        """
        Move negations inward using De Morgan's laws.
        
        ¬(A ∧ B) becomes ¬A ∨ ¬B
        ¬(A ∨ B) becomes ¬A ∧ ¬B
        ¬¬A becomes A
        ¬∀x.P(x) becomes ∃x.¬P(x)
        ¬∃x.P(x) becomes ∀x.¬P(x)
        
        Args:
            formula: The formula to transform
            
        Returns:
            The transformed formula
        """
        if isinstance(formula, ConnectiveNode):
            if formula.connective_type == "NOT":
                subformula = formula.operands[0]
                
                # Double negation: ¬¬A becomes A
                if isinstance(subformula, ConnectiveNode) and subformula.connective_type == "NOT":
                    return self._move_negations_inward(subformula.operands[0])
                
                # De Morgan's laws
                elif isinstance(subformula, ConnectiveNode) and subformula.connective_type == "AND":
                    # ¬(A ∧ B) becomes ¬A ∨ ¬B
                    negated_operands = [
                        ConnectiveNode("NOT", [op], op.type) for op in subformula.operands
                    ]
                    return ConnectiveNode(
                        "OR",
                        [self._move_negations_inward(op) for op in negated_operands],
                        formula.type
                    )
                
                elif isinstance(subformula, ConnectiveNode) and subformula.connective_type == "OR":
                    # ¬(A ∨ B) becomes ¬A ∧ ¬B
                    negated_operands = [
                        ConnectiveNode("NOT", [op], op.type) for op in subformula.operands
                    ]
                    return ConnectiveNode(
                        "AND",
                        [self._move_negations_inward(op) for op in negated_operands],
                        formula.type
                    )
                
                # Quantifier negation
                elif isinstance(subformula, QuantifierNode):
                    if subformula.quantifier_type == "FORALL":
                        # ¬∀x.P(x) becomes ∃x.¬P(x)
                        negated_scope = ConnectiveNode("NOT", [subformula.scope], subformula.scope.type)
                        return QuantifierNode(
                            "EXISTS",
                            list(subformula.bound_variables),
                            self._move_negations_inward(negated_scope),
                            formula.type
                        )
                    
                    elif subformula.quantifier_type == "EXISTS":
                        # ¬∃x.P(x) becomes ∀x.¬P(x)
                        negated_scope = ConnectiveNode("NOT", [subformula.scope], subformula.scope.type)
                        return QuantifierNode(
                            "FORALL",
                            list(subformula.bound_variables),
                            self._move_negations_inward(negated_scope),
                            formula.type
                        )
                
                # For other negated formulas, keep the negation but process the subformula
                return ConnectiveNode(
                    "NOT",
                    [self._move_negations_inward(subformula)],
                    formula.type
                )
            
            else:
                # Process other connectives recursively
                new_operands = [self._move_negations_inward(op) for op in formula.operands]
                return ConnectiveNode(formula.connective_type, new_operands, formula.type)
        
        elif isinstance(formula, QuantifierNode):
            # Process the scope recursively
            new_scope = self._move_negations_inward(formula.scope)
            return QuantifierNode(
                formula.quantifier_type,
                list(formula.bound_variables),
                new_scope,
                formula.type
            )
        
        # For other node types, return as is
        return formula
    
    def _standardize_variables(self, formula: AST_Node) -> AST_Node:
        """
        Standardize variables apart.
        
        This ensures that each quantifier binds a unique variable.
        
        Args:
            formula: The formula to transform
            
        Returns:
            The transformed formula
        """
        # Map from original variable IDs to new variable nodes
        var_map = {}
        
        def process_node(node: AST_Node) -> AST_Node:
            if isinstance(node, QuantifierNode):
                # Create new variables for this quantifier
                new_bound_vars = []
                substitution = {}
                
                for var in node.bound_variables:
                    new_var_id = self.next_var_id
                    self.next_var_id += 1
                    new_var = VariableNode(var.name, new_var_id, var.type)
                    new_bound_vars.append(new_var)
                    substitution[var] = new_var
                    var_map[var.var_id] = new_var
                
                # Process the scope with the new variables
                new_scope = node.scope.substitute(substitution)
                processed_scope = process_node(new_scope)
                
                return QuantifierNode(
                    node.quantifier_type,
                    new_bound_vars,
                    processed_scope,
                    node.type
                )
            
            elif isinstance(node, ConnectiveNode):
                new_operands = [process_node(op) for op in node.operands]
                return ConnectiveNode(node.connective_type, new_operands, node.type)
            
            elif isinstance(node, ApplicationNode):
                new_operator = process_node(node.operator)
                new_arguments = [process_node(arg) for arg in node.arguments]
                return ApplicationNode(new_operator, new_arguments, node.type)
            
            elif isinstance(node, VariableNode):
                # If this is a free variable (not in var_map), keep it as is
                if node.var_id in var_map:
                    return var_map[node.var_id]
                return node
            
            # For other node types, return as is
            return node
        
        return process_node(formula)
    
    def _skolemize(self, formula: AST_Node) -> AST_Node:
        """
        Skolemize existential quantifiers.
        
        This replaces existentially quantified variables with Skolem functions
        that depend on the universally quantified variables in whose scope they appear.
        
        Args:
            formula: The formula to transform
            
        Returns:
            The transformed formula
        """
        # Keep track of universal variables in scope
        universal_vars = []
        
        def process_node(node: AST_Node) -> AST_Node:
            if isinstance(node, QuantifierNode):
                if node.quantifier_type == "FORALL":
                    # Add universal variables to the scope
                    universal_vars.extend(node.bound_variables)
                    processed_scope = process_node(node.scope)
                    # Remove these variables from scope when done
                    for _ in range(len(node.bound_variables)):
                        universal_vars.pop()
                    
                    return QuantifierNode(
                        "FORALL",
                        list(node.bound_variables),
                        processed_scope,
                        node.type
                    )
                
                elif node.quantifier_type == "EXISTS":
                    # Replace existential variables with Skolem functions
                    substitution = {}
                    
                    for var in node.bound_variables:
                        # Create a Skolem function or constant
                        if universal_vars:
                            # Create a Skolem function that depends on universal variables
                            skolem_name = f"sk_{self.next_skolem_id}"
                            self.next_skolem_id += 1
                            
                            # Create the function symbol
                            skolem_func = ConstantNode(skolem_name, var.type)
                            
                            # Create the application of the function to universal variables
                            skolem_term = ApplicationNode(
                                skolem_func,
                                universal_vars.copy(),
                                var.type
                            )
                            
                            substitution[var] = skolem_term
                        else:
                            # Create a Skolem constant (no universal variables in scope)
                            skolem_name = f"sk_{self.next_skolem_id}"
                            self.next_skolem_id += 1
                            skolem_const = ConstantNode(skolem_name, var.type)
                            substitution[var] = skolem_const
                    
                    # Apply the substitution to the scope and process it
                    new_scope = node.scope.substitute(substitution)
                    return process_node(new_scope)
            
            elif isinstance(node, ConnectiveNode):
                new_operands = [process_node(op) for op in node.operands]
                return ConnectiveNode(node.connective_type, new_operands, node.type)
            
            elif isinstance(node, ApplicationNode):
                new_operator = process_node(node.operator)
                new_arguments = [process_node(arg) for arg in node.arguments]
                return ApplicationNode(new_operator, new_arguments, node.type)
            
            # For other node types, return as is
            return node
        
        return process_node(formula)
    
    def _drop_quantifiers(self, formula: AST_Node) -> AST_Node:
        """
        Drop universal quantifiers.
        
        After skolemization, all remaining quantifiers are universal and can be dropped.
        
        Args:
            formula: The formula to transform
            
        Returns:
            The transformed formula
        """
        if isinstance(formula, QuantifierNode):
            if formula.quantifier_type == "FORALL":
                # Drop the quantifier and process the scope
                return self._drop_quantifiers(formula.scope)
            else:
                # This shouldn't happen after skolemization
                logger.warning(f"Unexpected existential quantifier after skolemization: {formula}")
                return formula
        
        elif isinstance(formula, ConnectiveNode):
            new_operands = [self._drop_quantifiers(op) for op in formula.operands]
            return ConnectiveNode(formula.connective_type, new_operands, formula.type)
        
        elif isinstance(formula, ApplicationNode):
            new_operator = self._drop_quantifiers(formula.operator)
            new_arguments = [self._drop_quantifiers(arg) for arg in formula.arguments]
            return ApplicationNode(new_operator, new_arguments, formula.type)
        
        # For other node types, return as is
        return formula
    
    def _distribute_or_over_and(self, formula: AST_Node) -> AST_Node:
        """
        Distribute disjunctions over conjunctions.
        
        (A ∨ (B ∧ C)) becomes ((A ∨ B) ∧ (A ∨ C))
        ((A ∧ B) ∨ C) becomes ((A ∨ C) ∧ (B ∨ C))
        
        Args:
            formula: The formula to transform
            
        Returns:
            The transformed formula
        """
        if isinstance(formula, ConnectiveNode):
            if formula.connective_type == "OR":
                # First, recursively process all operands
                processed_operands = [self._distribute_or_over_and(op) for op in formula.operands]
                
                # Check if any operand is a conjunction
                for i, operand in enumerate(processed_operands):
                    if isinstance(operand, ConnectiveNode) and operand.connective_type == "AND":
                        # Found a conjunction, distribute OR over it
                        other_operands = processed_operands[:i] + processed_operands[i+1:]
                        
                        # Create a disjunction for each conjunct
                        new_conjuncts = []
                        for conjunct in operand.operands:
                            new_disjunction = ConnectiveNode(
                                "OR",
                                other_operands + [conjunct],
                                formula.type
                            )
                            # Recursively process the new disjunction
                            new_conjuncts.append(self._distribute_or_over_and(new_disjunction))
                        
                        # Return the conjunction of the new disjunctions
                        return ConnectiveNode("AND", new_conjuncts, formula.type)
                
                # If no conjunctions were found, return the processed formula
                return ConnectiveNode("OR", processed_operands, formula.type)
            
            elif formula.connective_type == "AND":
                # Process all operands recursively
                new_operands = [self._distribute_or_over_and(op) for op in formula.operands]
                return ConnectiveNode("AND", new_operands, formula.type)
            
            else:
                # Process other connectives recursively
                new_operands = [self._distribute_or_over_and(op) for op in formula.operands]
                return ConnectiveNode(formula.connective_type, new_operands, formula.type)
        
        # For other node types, return as is
        return formula
    
    def _extract_clauses(self, formula: AST_Node) -> List[Clause]:
        """
        Extract clauses from a formula in CNF.
        
        Args:
            formula: The formula in CNF
            
        Returns:
            A list of clauses
        """
        clauses = []
        
        # If the formula is a conjunction, extract clauses from each conjunct
        if isinstance(formula, ConnectiveNode) and formula.connective_type == "AND":
            for operand in formula.operands:
                clauses.extend(self._extract_clauses(operand))
            return clauses
        
        # Otherwise, extract a single clause
        literals = self._extract_literals(formula)
        return [Clause(frozenset(literals))]
    
    def _extract_literals(self, formula: AST_Node) -> List[Literal]:
        """
        Extract literals from a disjunction.
        
        Args:
            formula: The formula (a disjunction or a single literal)
            
        Returns:
            A list of literals
        """
        if isinstance(formula, ConnectiveNode) and formula.connective_type == "OR":
            # Collect literals from each disjunct
            literals = []
            for operand in formula.operands:
                literals.extend(self._extract_literals(operand))
            return literals
        
        elif isinstance(formula, ConnectiveNode) and formula.connective_type == "NOT":
            # Negated atom
            return [Literal(formula.operands[0], True)]
        
        else:
            # Positive atom
            return [Literal(formula)]


class ResolutionProver(BaseProver):
    """
    Prover using resolution for FOL and propositional logic.
    
    This prover implements the resolution inference rule for First-Order Logic (FOL)
    and propositional logic. It converts input formulae into Conjunctive Normal Form (CNF)
    and applies various resolution strategies to find a refutation.
    """
    
    def __init__(self, kr_system_interface: KnowledgeStoreInterface,
                unification_engine: UnificationEngine,
                cnf_converter: Optional[CNFConverter] = None):
        """
        Initialize the resolution prover.
        
        Args:
            kr_system_interface: Interface to the Knowledge Representation system
            unification_engine: Engine for unifying logical expressions
            cnf_converter: Optional converter for Conjunctive Normal Form
        """
        self.kr_system_interface = kr_system_interface
        self.unification_engine = unification_engine
        self.cnf_converter = cnf_converter or CNFConverter(unification_engine)
        self.next_clause_id = 0
    
    @property
    def name(self) -> str:
        """Get the name of this prover."""
        return "ResolutionProver"
    
    @property
    def capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this prover."""
        capabilities = super().capabilities.copy()
        capabilities.update({
            "first_order_logic": True,
            "propositional_logic": True,
            "equality": True,
            "uninterpreted_functions": True
        })
        return capabilities
    
    def can_handle(self, goal_ast: AST_Node, context_asts: Set[AST_Node]) -> bool:
        """
        Determine if this prover can handle the given goal and context.
        
        The resolution prover can handle first-order logic and propositional logic goals.
        
        Args:
            goal_ast: The goal to prove
            context_asts: The set of context assertions
            
        Returns:
            True if this prover can handle the given goal and context, False otherwise
        """
        # Check if the goal and context contain modal operators, arithmetic, or constraints
        from godelOS.inference_engine.coordinator import InferenceCoordinator
        coordinator = InferenceCoordinator(self.kr_system_interface, {})
        
        contains_modal = coordinator._contains_modal_operator(goal_ast)
        contains_arithmetic = coordinator._contains_arithmetic(goal_ast)
        contains_constraints = coordinator._contains_constraints(goal_ast)
        
        # Check context as well
        for ast in context_asts:
            if coordinator._contains_modal_operator(ast) or \
               coordinator._contains_arithmetic(ast) or \
               coordinator._contains_constraints(ast):
                return False
        
        return not (contains_modal or contains_arithmetic or contains_constraints)
    
    def prove(self, goal_ast: AST_Node, context_asts: Set[AST_Node],
             resources: Optional[ResourceLimits] = None) -> ProofObject:
        """
        Attempt to prove a goal using resolution.
        
        This method implements the full resolution algorithm, including:
        1. Converting the goal and context to CNF
        2. Negating the goal
        3. Applying resolution strategies to find a refutation
        
        Args:
            goal_ast: The goal to prove
            context_asts: The set of context assertions
            resources: Optional resource limits for the proof attempt
            
        Returns:
            A ProofObject representing the result of the proof attempt
        """
        start_time = time.time()
        
        # Set default resource limits if none provided
        if resources is None:
            resources = ResourceLimits(time_limit_ms=10000, depth_limit=100, nodes_limit=10000)
        
        logger.info(f"ResolutionProver attempting to prove: {goal_ast}")
        logger.info(f"Context size: {len(context_asts)}")
        
        try:
            # Step 1: Negate the goal
            negated_goal = self._negate_formula(goal_ast)
            logger.debug(f"Negated goal: {negated_goal}")
            
            # Step 2: Convert all formulas to CNF
            axiom_clauses = []
            for axiom in context_asts:
                axiom_clauses.extend(self.cnf_converter.convert_to_cnf(axiom))
            
            goal_clauses = self.cnf_converter.convert_to_cnf(negated_goal)
            
            # Assign IDs to all clauses
            all_clauses = []
            for clause in axiom_clauses:
                all_clauses.append(Clause(
                    clause.literals,
                    "axiom",
                    (),
                    self.next_clause_id
                ))
                self.next_clause_id += 1
            
            for clause in goal_clauses:
                all_clauses.append(Clause(
                    clause.literals,
                    "negated_goal",
                    (),
                    self.next_clause_id
                ))
                self.next_clause_id += 1
            
            logger.info(f"Total clauses: {len(all_clauses)}")
            for clause in all_clauses:
                logger.debug(f"Clause {clause.clause_id}: {clause}")
            
            # Step 3: Apply resolution
            strategy = resources.get_limit("strategy", "set_of_support")
            result = self._resolve_clauses(all_clauses, resources, strategy)
            
            # Calculate time taken
            end_time = time.time()
            time_taken_ms = (end_time - start_time) * 1000
            
            # Return the proof object
            if result.proof_found:
                # Create proof steps
                proof_steps = self._create_proof_steps(result.proof_trace, all_clauses)
                
                return ProofObject.create_success(
                    conclusion_ast=goal_ast,
                    proof_steps=proof_steps,
                    used_axioms_rules=context_asts,
                    inference_engine_used=self.name,
                    time_taken_ms=time_taken_ms,
                    resources_consumed={
                        "clauses_generated": result.clauses_generated,
                        "resolution_steps": result.resolution_steps,
                        "max_depth": result.max_depth
                    }
                )
            else:
                status_message = "Proof not found"
                if result.resource_limit_reached:
                    status_message = f"Resource limit reached: {result.limit_type}"
                
                return ProofObject.create_failure(
                    status_message=status_message,
                    inference_engine_used=self.name,
                    time_taken_ms=time_taken_ms,
                    resources_consumed={
                        "clauses_generated": result.clauses_generated,
                        "resolution_steps": result.resolution_steps,
                        "max_depth": result.max_depth
                    }
                )
                
        except Exception as e:
            logger.error(f"Error during proof: {str(e)}", exc_info=True)
            end_time = time.time()
            time_taken_ms = (end_time - start_time) * 1000
            
            return ProofObject.create_failure(
                status_message=f"Error: {str(e)}",
                inference_engine_used=self.name,
                time_taken_ms=time_taken_ms,
                resources_consumed={}
            )
    
    def _negate_formula(self, formula: AST_Node) -> AST_Node:
        """
        Negate a formula.
        
        Args:
            formula: The formula to negate
            
        Returns:
            The negated formula
        """
        return ConnectiveNode("NOT", [formula], formula.type)
    
    @dataclass
    class ResolutionResult:
        """Result of the resolution process."""
        proof_found: bool = False
        resource_limit_reached: bool = False
        limit_type: str = ""
        clauses_generated: int = 0
        resolution_steps: int = 0
        max_depth: int = 0
        proof_trace: List[int] = field(default_factory=list)
    
    def _resolve_clauses(self, clauses: List[Clause], resources: ResourceLimits,
                        strategy: str = "set_of_support") -> ResolutionResult:
        """
        Apply resolution to a set of clauses.
        
        Args:
            clauses: The clauses to resolve
            resources: Resource limits for the proof attempt
            strategy: The resolution strategy to use
            
        Returns:
            A ResolutionResult object containing the result of the resolution process
        """
        result = self.ResolutionResult()
        
        # Initialize clause sets based on the strategy
        if strategy == "set_of_support":
            # Separate axioms and goal clauses
            axiom_clauses = [c for c in clauses if c.source == "axiom"]
            goal_clauses = [c for c in clauses if c.source == "negated_goal"]
            
            # The set of support initially contains the goal clauses
            sos = set(goal_clauses)
            usable = set(axiom_clauses)
        else:
            # For other strategies, all clauses are usable
            sos = set(clauses)
            usable = set()
        
        # Keep track of all generated clauses to avoid duplicates
        all_clauses = {c.clause_id: c for c in clauses}
        
        # Keep track of the maximum depth of the proof
        result.max_depth = 0
        
        # Main resolution loop
        while sos and not result.proof_found and not result.resource_limit_reached:
            # Check resource limits
            result.resolution_steps += 1
            
            if resources.time_limit_ms is not None:
                elapsed_time = (time.time() - time.time()) * 1000  # This is a placeholder
                if elapsed_time > resources.time_limit_ms:
                    result.resource_limit_reached = True
                    result.limit_type = "time_limit"
                    break
            
            if resources.nodes_limit is not None and result.clauses_generated > resources.nodes_limit:
                result.resource_limit_reached = True
                result.limit_type = "nodes_limit"
                break
            
            if resources.depth_limit is not None and result.max_depth > resources.depth_limit:
                result.resource_limit_reached = True
                result.limit_type = "depth_limit"
                break
            
            # Select a clause from the set of support
            given_clause = self._select_clause(sos, strategy)
            sos.remove(given_clause)
            
            # Add the given clause to the usable set
            usable.add(given_clause)
            
            # Try to resolve the given clause with all usable clauses
            for clause in usable:
                # Skip if the clause is the given clause itself
                if clause.clause_id == given_clause.clause_id:
                    continue
                
                # Try to resolve the two clauses
                resolvents = self._resolve_pair(given_clause, clause)
                
                # Process the resolvents
                for resolvent in resolvents:
                    # Check if the resolvent is the empty clause (contradiction found)
                    if resolvent.is_empty():
                        result.proof_found = True
                        result.proof_trace = self._trace_proof(resolvent, all_clauses)
                        return result
                    
                    # Check if the resolvent is a tautology (always true)
                    if self._is_tautology(resolvent):
                        continue
                    
                    # Check if the resolvent is a duplicate
                    is_duplicate = False
                    for existing_clause in all_clauses.values():
                        if self._clauses_equivalent(resolvent, existing_clause):
                            is_duplicate = True
                            break
                    
                    if is_duplicate:
                        continue
                    
                    # Add the resolvent to the set of support and all clauses
                    new_clause = Clause(
                        resolvent.literals,
                        "derived",
                        (given_clause.clause_id, clause.clause_id),
                        self.next_clause_id
                    )
                    self.next_clause_id += 1
                    
                    sos.add(new_clause)
                    all_clauses[new_clause.clause_id] = new_clause
                    result.clauses_generated += 1
                    
                    # Update the maximum depth
                    depth = max(self._get_clause_depth(given_clause, all_clauses),
                               self._get_clause_depth(clause, all_clauses)) + 1
                    result.max_depth = max(result.max_depth, depth)
        
        return result
    
    def _select_clause(self, clauses: Set[Clause], strategy: str) -> Clause:
        """
        Select a clause based on the given strategy.
        
        Args:
            clauses: The set of clauses to select from
            strategy: The selection strategy
            
        Returns:
            The selected clause
        """
        if strategy == "unit_preference":
            # Prefer unit clauses
            for clause in clauses:
                if clause.is_unit():
                    return clause
        
        # Default: select the first clause (arbitrary)
        return next(iter(clauses))
    
    def _resolve_pair(self, clause1: Clause, clause2: Clause) -> List[Clause]:
        """
        Resolve two clauses.
        
        Args:
            clause1: The first clause
            clause2: The second clause
            
        Returns:
            A list of resolvent clauses
        """
        resolvents = []
        
        # Try to resolve each literal in clause1 with each literal in clause2
        for lit1 in clause1.literals:
            for lit2 in clause2.literals:
                # Check if the literals have opposite polarity
                if lit1.is_negated != lit2.is_negated:
                    # Try to unify the atoms
                    bindings, errors = self.unification_engine.unify(
                        lit1.atom, lit2.atom, None, "FIRST_ORDER"
                    )
                    
                    if bindings is not None:
                        # Unification successful, create the resolvent
                        new_literals = set()
                        
                        # Add literals from clause1 (except lit1)
                        for l in clause1.literals:
                            if l != lit1:
                                # Apply bindings to the literal
                                new_atom = self._apply_bindings(l.atom, bindings)
                                new_literals.add(Literal(new_atom, l.is_negated))
                        
                        # Add literals from clause2 (except lit2)
                        for l in clause2.literals:
                            if l != lit2:
                                # Apply bindings to the literal
                                new_atom = self._apply_bindings(l.atom, bindings)
                                new_literals.add(Literal(new_atom, l.is_negated))
                        
                        # Create the resolvent clause
                        resolvent = Clause(frozenset(new_literals))
                        resolvents.append(resolvent)
        
        return resolvents
    
    def _apply_bindings(self, node: AST_Node, bindings: Dict[int, AST_Node]) -> AST_Node:
        """
        Apply variable bindings to an AST node.
        
        Args:
            node: The AST node to which bindings should be applied
            bindings: The variable bindings to apply
            
        Returns:
            A new AST node with the bindings applied
        """
        # Convert the bindings from var_id to VariableNode
        substitution = {}
        
        # Helper function to find all variables in a node
        def collect_variables(n: AST_Node) -> List[VariableNode]:
            if isinstance(n, VariableNode):
                return [n]
            
            variables = []
            # For each child node, collect variables recursively
            if isinstance(n, ApplicationNode):
                variables.extend(collect_variables(n.operator))
                for arg in n.arguments:
                    variables.extend(collect_variables(arg))
            elif isinstance(n, ConnectiveNode):
                for operand in n.operands:
                    variables.extend(collect_variables(operand))
            elif isinstance(n, QuantifierNode):
                # Skip bound variables
                bound_var_ids = {var.var_id for var in n.bound_variables}
                scope_vars = collect_variables(n.scope)
                variables.extend([var for var in scope_vars if var.var_id not in bound_var_ids])
            
            return variables
        
        # Find all variables in the node
        all_vars = collect_variables(node)
        
        # Create substitution dictionary
        for var in all_vars:
            if var.var_id in bindings:
                substitution[var] = bindings[var.var_id]
        
        # If no substitutions are needed, return the original node
        if not substitution:
            return node
        
        # Apply the substitutions
        return node.substitute(substitution)
    
    def _is_tautology(self, clause: Clause) -> bool:
        """
        Check if a clause is a tautology.
        
        A clause is a tautology if it contains both a literal and its negation.
        
        Args:
            clause: The clause to check
            
        Returns:
            True if the clause is a tautology, False otherwise
        """
        for lit1 in clause.literals:
            for lit2 in clause.literals:
                if lit1.is_negated != lit2.is_negated:
                    # Try to unify the atoms
                    bindings, errors = self.unification_engine.unify(
                        lit1.atom, lit2.atom, None, "FIRST_ORDER"
                    )
                    
                    if bindings is not None:
                        # The atoms unify, so the clause contains a literal and its negation
                        return True
        
        return False
    
    def _clauses_equivalent(self, clause1: Clause, clause2: Clause) -> bool:
        """
        Check if two clauses are equivalent.
        
        Args:
            clause1: The first clause
            clause2: The second clause
            
        Returns:
            True if the clauses are equivalent, False otherwise
        """
        # Quick check: if the clauses have different numbers of literals, they're not equivalent
        if len(clause1.literals) != len(clause2.literals):
            return False
        
        # Check if each literal in clause1 has a corresponding literal in clause2
        for lit1 in clause1.literals:
            found_match = False
            for lit2 in clause2.literals:
                if lit1.is_negated == lit2.is_negated:
                    # Try to unify the atoms
                    bindings, errors = self.unification_engine.unify(
                        lit1.atom, lit2.atom, None, "FIRST_ORDER"
                    )
                    
                    if bindings is not None:
                        found_match = True
                        break
            
            if not found_match:
                return False
        
        return True
    
    def _get_clause_depth(self, clause: Clause, all_clauses: Dict[int, Clause]) -> int:
        """
        Get the depth of a clause in the proof tree.
        
        Args:
            clause: The clause to check
            all_clauses: Dictionary of all clauses by ID
            
        Returns:
            The depth of the clause
        """
        if not clause.parent_ids:
            return 0
        
        return 1 + max(self._get_clause_depth(all_clauses[parent_id], all_clauses)
                      for parent_id in clause.parent_ids)
    
    def _trace_proof(self, empty_clause: Clause, all_clauses: Dict[int, Clause]) -> List[int]:
        """
        Trace the proof from the empty clause back to the original clauses.
        
        Args:
            empty_clause: The empty clause (contradiction)
            all_clauses: Dictionary of all clauses by ID
            
        Returns:
            A list of clause IDs in the proof trace
        """
        trace = [empty_clause.clause_id]
        queue = list(empty_clause.parent_ids)
        
        while queue:
            clause_id = queue.pop(0)
            if clause_id not in trace:
                trace.append(clause_id)
                queue.extend(all_clauses[clause_id].parent_ids)
        
        return trace
    
    def _create_proof_steps(self, proof_trace: List[int], all_clauses: Dict[int, Clause]) -> List[ProofStepNode]:
        """
        Create proof steps from a proof trace.
        
        Args:
            proof_trace: The proof trace (list of clause IDs)
            all_clauses: Dictionary of all clauses by ID
            
        Returns:
            A list of ProofStepNode objects
        """
        steps = []
        
        # Helper function to convert a clause to an AST
        def clause_to_ast(clause: Clause) -> AST_Node:
            if clause.is_empty():
                # Empty clause (contradiction)
                return ConstantNode("false", clause.literals[0].atom.type if clause.literals else None)
            
            # Convert literals to AST nodes
            literals = []
            for lit in clause.literals:
                if lit.is_negated:
                    literals.append(ConnectiveNode("NOT", [lit.atom], lit.atom.type))
                else:
                    literals.append(lit.atom)
            
            # If there's only one literal, return it
            if len(literals) == 1:
                return literals[0]
            
            # Otherwise, create a disjunction
            return ConnectiveNode("OR", literals, literals[0].type)
        
        # Create a step for each clause in the proof trace
        for i, clause_id in enumerate(proof_trace):
            clause = all_clauses[clause_id]
            
            # Create the formula for this step
            formula = clause_to_ast(clause)
            
            # Determine the rule name and premises
            if not clause.parent_ids:
                # Original clause (axiom or negated goal)
                rule_name = "Given"
                premises = []
                explanation = f"Original {clause.source} clause"
            else:
                # Derived clause
                rule_name = "Resolution"
                premises = [proof_trace.index(parent_id) for parent_id in clause.parent_ids if parent_id in proof_trace]
                explanation = f"Resolvent of clauses {', '.join(str(p) for p in premises)}"
            
            # Create the proof step
            step = ProofStepNode(
                formula=formula,
                rule_name=rule_name,
                premises=premises,
                explanation=explanation
            )
            
            steps.append(step)
        
        return steps

class ResolutionProver(BaseProver):
    """
    Prover using resolution for FOL and propositional logic.
    
    This prover implements the resolution inference rule for First-Order Logic (FOL)
    and propositional logic. It converts input formulae into Conjunctive Normal Form (CNF)
    and applies various resolution strategies to find a refutation.
    """
    
    def __init__(self, kr_system_interface: KnowledgeStoreInterface, 
                unification_engine: UnificationEngine,
                cnf_converter: Any = None):
        """
        Initialize the resolution prover.
        
        Args:
            kr_system_interface: Interface to the Knowledge Representation system
            unification_engine: Engine for unifying logical expressions
            cnf_converter: Optional converter for Conjunctive Normal Form
        """
        self.kr_system_interface = kr_system_interface
        self.unification_engine = unification_engine
        self.cnf_converter = cnf_converter
    
    @property
    def name(self) -> str:
        """Get the name of this prover."""
        return "ResolutionProver"
    
    @property
    def capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this prover."""
        capabilities = super().capabilities.copy()
        capabilities.update({
            "first_order_logic": True,
            "propositional_logic": True,
            "equality": True,
            "uninterpreted_functions": True
        })
        return capabilities
    
    def can_handle(self, goal_ast: AST_Node, context_asts: Set[AST_Node]) -> bool:
        """
        Determine if this prover can handle the given goal and context.
        
        The resolution prover can handle first-order logic and propositional logic goals.
        
        Args:
            goal_ast: The goal to prove
            context_asts: The set of context assertions
            
        Returns:
            True if this prover can handle the given goal and context, False otherwise
        """
        # This is a simplified check that would need to be expanded in a full implementation
        # to properly analyze the goal and context for compatibility with resolution
        
        # For now, assume we can handle the goal if it doesn't contain modal operators,
        # arithmetic, or constraints (which would be handled by other provers)
        from godelOS.inference_engine.coordinator import InferenceCoordinator
        coordinator = InferenceCoordinator(self.kr_system_interface, {})
        
        contains_modal = coordinator._contains_modal_operator(goal_ast)
        contains_arithmetic = coordinator._contains_arithmetic(goal_ast)
        contains_constraints = coordinator._contains_constraints(goal_ast)
        
        return not (contains_modal or contains_arithmetic or contains_constraints)
    
    def prove(self, goal_ast: AST_Node, context_asts: Set[AST_Node], 
             resources: Optional[ResourceLimits] = None) -> ProofObject:
        """
        Attempt to prove a goal using resolution.
        
        This method would implement the full resolution algorithm, including:
        1. Converting the goal and context to CNF
        2. Negating the goal
        3. Applying resolution strategies to find a refutation
        
        Args:
            goal_ast: The goal to prove
            context_asts: The set of context assertions
            resources: Optional resource limits for the proof attempt
            
        Returns:
            A ProofObject representing the result of the proof attempt
        """
        # This is a placeholder implementation that would be expanded in the future
        
        logger.info(f"ResolutionProver attempting to prove: {goal_ast}")
        
        # For now, just return a failure proof object
        return ProofObject.create_failure(
            status_message="ResolutionProver not fully implemented yet",
            inference_engine_used=self.name,
            time_taken_ms=0.0,
            resources_consumed={}
        )