"""
Unification Engine implementation.

This module implements the UnificationEngine class, which is responsible for
determining if two logical expressions (ASTs) can be made syntactically identical
by substituting variables with terms, and for producing the Most General Unifier (MGU)
if unification is possible.

The engine supports both first-order and higher-order unification, with proper
handling of bound variables, occurs check, and alpha/beta/eta conversions.
"""

from typing import Dict, List, Optional, Set, Tuple, Union, cast
import copy
from collections import defaultdict

from godelOS.core_kr.ast.nodes import (
    AST_Node, ConstantNode, VariableNode, ApplicationNode,
    QuantifierNode, ConnectiveNode, ModalOpNode, LambdaNode, DefinitionNode
)
from godelOS.core_kr.type_system.manager import TypeSystemManager


class Error:
    """An error during unification."""
    
    def __init__(self, message: str, node1: Optional[AST_Node] = None, node2: Optional[AST_Node] = None):
        """
        Initialize an error.
        
        Args:
            message: The error message
            node1: Optional first node involved in the error
            node2: Optional second node involved in the error
        """
        self.message = message
        self.node1 = node1
        self.node2 = node2
    
    def __str__(self) -> str:
        return self.message


class UnificationEngine:
    """
    Engine for unifying logical expressions.
    
    Determines if two logical expressions (ASTs) can be made syntactically identical
    by substituting variables with terms, and produces the Most General Unifier (MGU)
    if unification is possible.
    
    Supports both first-order and higher-order unification, with proper handling of
    bound variables, occurs check, and alpha/beta/eta conversions.
    """
    
    def __init__(self, type_system: TypeSystemManager):
        """
        Initialize the unification engine.
        
        Args:
            type_system: The type system manager for type checking and inference
        """
        self.type_system = type_system
        self._next_var_id = 10000  # Start with a high ID to avoid conflicts
    
    def unify(self, ast1: AST_Node, ast2: AST_Node,
              current_bindings: Optional[Dict[int, AST_Node]] = None,
              mode: str = "FIRST_ORDER") -> Tuple[Optional[Dict[int, AST_Node]], List[Error]]:
        """
        Unify two AST nodes.
        
        Attempts to find a substitution that makes the two AST nodes syntactically
        identical. If successful, returns the Most General Unifier (MGU).
        
        Args:
            ast1: The first AST node
            ast2: The second AST node
            current_bindings: Optional current variable bindings
            mode: The unification mode ("FIRST_ORDER" or "HIGHER_ORDER")
            
        Returns:
            The Most General Unifier (MGU) as a mapping from variable IDs to AST nodes,
            or None if unification is not possible, and a list of errors
        """
        bindings = current_bindings.copy() if current_bindings else {}
        errors = []
        
        # Apply current bindings to the input ASTs
        if bindings:
            ast1 = self._apply_bindings(ast1, bindings)
            ast2 = self._apply_bindings(ast2, bindings)
        
        # Check if the types are compatible
        if not self.type_system.is_subtype(ast1.type, ast2.type) and not self.type_system.is_subtype(ast2.type, ast1.type):
            errors.append(Error(f"Type mismatch: {ast1.type} and {ast2.type}", ast1, ast2))
            return None, errors
        
        # Variable cases
        if isinstance(ast1, VariableNode):
            return self._unify_variable(ast1, ast2, bindings, mode, errors)
        
        if isinstance(ast2, VariableNode):
            return self._unify_variable(ast2, ast1, bindings, mode, errors)
        
        # Constant case
        if isinstance(ast1, ConstantNode) and isinstance(ast2, ConstantNode):
            if ast1.name == ast2.name:
                return bindings, errors
            else:
                errors.append(Error(f"Constant mismatch: {ast1.name} and {ast2.name}", ast1, ast2))
                return None, errors
        
        # Application case
        if isinstance(ast1, ApplicationNode) and isinstance(ast2, ApplicationNode):
            return self._unify_application(ast1, ast2, bindings, mode, errors)
        
        # Connective case
        if isinstance(ast1, ConnectiveNode) and isinstance(ast2, ConnectiveNode):
            return self._unify_connective(ast1, ast2, bindings, mode, errors)
        
        # Quantifier case
        if isinstance(ast1, QuantifierNode) and isinstance(ast2, QuantifierNode):
            return self._unify_quantifier(ast1, ast2, bindings, mode, errors)
        
        # Modal operator case
        if isinstance(ast1, ModalOpNode) and isinstance(ast2, ModalOpNode):
            return self._unify_modal_op(ast1, ast2, bindings, mode, errors)
        
        # Lambda case (higher-order only)
        if isinstance(ast1, LambdaNode) and isinstance(ast2, LambdaNode):
            if mode == "HIGHER_ORDER":
                return self._unify_lambda(ast1, ast2, bindings, errors)
            else:
                errors.append(Error("Lambda unification requires HIGHER_ORDER mode", ast1, ast2))
                return None, errors
                
        # Definition case
        if isinstance(ast1, DefinitionNode) and isinstance(ast2, DefinitionNode):
            return self._unify_definition(ast1, ast2, bindings, mode, errors)
        
        # If we get here, the nodes are of different types and can't be unified
        errors.append(Error(f"Node type mismatch: {type(ast1).__name__} and {type(ast2).__name__}", ast1, ast2))
        return None, errors
    
    def _apply_bindings(self, node: AST_Node, bindings: Dict[int, AST_Node]) -> AST_Node:
        """
        Apply variable bindings to an AST node.
        
        Args:
            node: The AST node to which bindings should be applied
            bindings: The variable bindings to apply
            
        Returns:
            A new AST node with the bindings applied
        """
        # If the node is a variable and it's in the bindings, return the replacement
        if isinstance(node, VariableNode) and node.var_id in bindings:
            return bindings[node.var_id]
        
        # For other node types, create a substitution dictionary for the substitute method
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
            elif isinstance(n, ModalOpNode):
                variables.extend(collect_variables(n.proposition))
                if n.agent_or_world:
                    variables.extend(collect_variables(n.agent_or_world))
            elif isinstance(n, LambdaNode):
                # Skip bound variables
                bound_var_ids = {var.var_id for var in n.bound_variables}
                body_vars = collect_variables(n.body)
                variables.extend([var for var in body_vars if var.var_id not in bound_var_ids])
            elif isinstance(n, DefinitionNode):
                variables.extend(collect_variables(n.definition_body_ast))
            
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
    
    def _unify_variable(self, var: VariableNode, term: AST_Node, bindings: Dict[int, AST_Node],
                        mode: str, errors: List[Error]) -> Tuple[Optional[Dict[int, AST_Node]], List[Error]]:
        """
        Unify a variable with a term.
        
        Args:
            var: The variable node
            term: The term to unify with
            bindings: Current variable bindings
            mode: The unification mode
            errors: List of errors
            
        Returns:
            Updated bindings and errors
        """
        var_id = var.var_id
        
        # If the variable is already bound, unify the binding with the term
        if var_id in bindings:
            return self.unify(bindings[var_id], term, bindings, mode)
        
        # If the term is the same variable, just return the current bindings
        if isinstance(term, VariableNode) and term.var_id == var_id:
            return bindings, errors
        
        # If the term is a variable that's already bound, unify with its binding
        if isinstance(term, VariableNode) and term.var_id in bindings:
            return self.unify(var, bindings[term.var_id], bindings, mode)
        
        # Occurs check (for first-order unification)
        if mode == "FIRST_ORDER" and self._occurs_check(var_id, term, bindings):
            errors.append(Error(f"Occurs check failed: {var.name} occurs in {term}", var, term))
            return None, errors
        
        # Bind the variable to the term
        new_bindings = bindings.copy()
        new_bindings[var_id] = term
        
        # Update existing bindings that point to this variable
        # This ensures transitive closure of bindings
        for vid, val in list(new_bindings.items()):
            if isinstance(val, VariableNode) and val.var_id == var_id:
                new_bindings[vid] = term
        
        return new_bindings, errors
    
    def _occurs_check(self, var_id: int, term: AST_Node, bindings: Dict[int, AST_Node]) -> bool:
        """
        Check if a variable occurs in a term.
        
        Args:
            var_id: The variable ID
            term: The term to check
            bindings: Current variable bindings
            
        Returns:
            True if the variable occurs in the term, False otherwise
        """
        if isinstance(term, VariableNode):
            if term.var_id == var_id:
                return True
            elif term.var_id in bindings:
                return self._occurs_check(var_id, bindings[term.var_id], bindings)
            else:
                return False
        
        if isinstance(term, ApplicationNode):
            if self._occurs_check(var_id, term.operator, bindings):
                return True
            for arg in term.arguments:
                if self._occurs_check(var_id, arg, bindings):
                    return True
            return False
        
        if isinstance(term, ConnectiveNode):
            for operand in term.operands:
                if self._occurs_check(var_id, operand, bindings):
                    return True
            return False
        
        if isinstance(term, QuantifierNode):
            # Check if the variable is bound by this quantifier
            for bound_var in term.bound_variables:
                if bound_var.var_id == var_id:
                    return False
            return self._occurs_check(var_id, term.scope, bindings)
        
        if isinstance(term, ModalOpNode):
            if term.agent_or_world and self._occurs_check(var_id, term.agent_or_world, bindings):
                return True
            return self._occurs_check(var_id, term.proposition, bindings)
        
        if isinstance(term, LambdaNode):
            # Check if the variable is bound by this lambda
            for bound_var in term.bound_variables:
                if bound_var.var_id == var_id:
                    return False
            return self._occurs_check(var_id, term.body, bindings)
        
        # For constants and other leaf nodes, the variable doesn't occur
        return False
    
    def _unify_application(self, app1: ApplicationNode, app2: ApplicationNode, 
                          bindings: Dict[int, AST_Node], mode: str, 
                          errors: List[Error]) -> Tuple[Optional[Dict[int, AST_Node]], List[Error]]:
        """
        Unify two application nodes.
        
        Args:
            app1: The first application node
            app2: The second application node
            bindings: Current variable bindings
            mode: The unification mode
            errors: List of errors
            
        Returns:
            Updated bindings and errors
        """
        # Check if the number of arguments match
        if len(app1.arguments) != len(app2.arguments):
            errors.append(Error(f"Argument count mismatch: {len(app1.arguments)} and {len(app2.arguments)}", app1, app2))
            return None, errors
        
        # Unify the operators
        operator_bindings, operator_errors = self.unify(app1.operator, app2.operator, bindings, mode)
        if operator_bindings is None:
            errors.extend(operator_errors)
            return None, errors
        
        # Unify the arguments
        arg_bindings = operator_bindings
        for i in range(len(app1.arguments)):
            arg_bindings, arg_errors = self.unify(app1.arguments[i], app2.arguments[i], arg_bindings, mode)
            if arg_bindings is None:
                errors.extend(arg_errors)
                return None, errors
        
        return arg_bindings, errors
    
    def _unify_connective(self, conn1: ConnectiveNode, conn2: ConnectiveNode, 
                         bindings: Dict[int, AST_Node], mode: str, 
                         errors: List[Error]) -> Tuple[Optional[Dict[int, AST_Node]], List[Error]]:
        """
        Unify two connective nodes.
        
        Args:
            conn1: The first connective node
            conn2: The second connective node
            bindings: Current variable bindings
            mode: The unification mode
            errors: List of errors
            
        Returns:
            Updated bindings and errors
        """
        # Check if the connective types match
        if conn1.connective_type != conn2.connective_type:
            errors.append(Error(f"Connective type mismatch: {conn1.connective_type} and {conn2.connective_type}", conn1, conn2))
            return None, errors
        
        # Check if the number of operands match
        if len(conn1.operands) != len(conn2.operands):
            errors.append(Error(f"Operand count mismatch: {len(conn1.operands)} and {len(conn2.operands)}", conn1, conn2))
            return None, errors
        
        # Unify the operands
        operand_bindings = bindings
        for i in range(len(conn1.operands)):
            operand_bindings, operand_errors = self.unify(conn1.operands[i], conn2.operands[i], operand_bindings, mode)
            if operand_bindings is None:
                errors.extend(operand_errors)
                return None, errors
        
        return operand_bindings, errors
    
    def _unify_quantifier(self, quant1: QuantifierNode, quant2: QuantifierNode,
                         bindings: Dict[int, AST_Node], mode: str,
                         errors: List[Error]) -> Tuple[Optional[Dict[int, AST_Node]], List[Error]]:
        """
        Unify two quantifier nodes.
        
        Handles alpha-equivalence by creating fresh variables for bound variables
        and then unifying the scopes.
        
        Args:
            quant1: The first quantifier node
            quant2: The second quantifier node
            bindings: Current variable bindings
            mode: The unification mode
            errors: List of errors
            
        Returns:
            Updated bindings and errors
        """
        # Check if the quantifier types match
        if quant1.quantifier_type != quant2.quantifier_type:
            errors.append(Error(f"Quantifier type mismatch: {quant1.quantifier_type} and {quant2.quantifier_type}", quant1, quant2))
            return None, errors
        
        # Check if the number of bound variables match
        if len(quant1.bound_variables) != len(quant2.bound_variables):
            errors.append(Error(f"Bound variable count mismatch: {len(quant1.bound_variables)} and {len(quant2.bound_variables)}", quant1, quant2))
            return None, errors
        
        # Create fresh variables for alpha-conversion
        fresh_vars = []
        var_subst1 = {}
        var_subst2 = {}
        
        for i in range(len(quant1.bound_variables)):
            var1 = quant1.bound_variables[i]
            var2 = quant2.bound_variables[i]
            
            # Create a fresh variable with the same type
            fresh_var_id = self._next_var_id
            self._next_var_id += 1
            fresh_var = VariableNode(f"?fresh_{fresh_var_id}", fresh_var_id, var1.type)
            fresh_vars.append(fresh_var)
            
            # Create substitutions for both quantifiers
            var_subst1[var1] = fresh_var
            var_subst2[var2] = fresh_var
        
        # Apply alpha-conversion to the scopes
        alpha_scope1 = quant1.scope.substitute(var_subst1)
        alpha_scope2 = quant2.scope.substitute(var_subst2)
        
        # Unify the alpha-converted scopes
        return self.unify(alpha_scope1, alpha_scope2, bindings, mode)
    
    def _unify_modal_op(self, modal1: ModalOpNode, modal2: ModalOpNode, 
                       bindings: Dict[int, AST_Node], mode: str, 
                       errors: List[Error]) -> Tuple[Optional[Dict[int, AST_Node]], List[Error]]:
        """
        Unify two modal operator nodes.
        
        Args:
            modal1: The first modal operator node
            modal2: The second modal operator node
            bindings: Current variable bindings
            mode: The unification mode
            errors: List of errors
            
        Returns:
            Updated bindings and errors
        """
        # Check if the modal operators match
        if modal1.modal_operator != modal2.modal_operator:
            errors.append(Error(f"Modal operator mismatch: {modal1.modal_operator} and {modal2.modal_operator}", modal1, modal2))
            return None, errors
        
        # Unify the agents/worlds if present
        if modal1.agent_or_world and modal2.agent_or_world:
            agent_bindings, agent_errors = self.unify(modal1.agent_or_world, modal2.agent_or_world, bindings, mode)
            if agent_bindings is None:
                errors.extend(agent_errors)
                return None, errors
            bindings = agent_bindings
        elif modal1.agent_or_world or modal2.agent_or_world:
            errors.append(Error("Agent/world presence mismatch", modal1, modal2))
            return None, errors
        
        # Unify the propositions
        return self.unify(modal1.proposition, modal2.proposition, bindings, mode)
    
    def _unify_lambda(self, lambda1: LambdaNode, lambda2: LambdaNode,
                     bindings: Dict[int, AST_Node],
                     errors: List[Error]) -> Tuple[Optional[Dict[int, AST_Node]], List[Error]]:
        """
        Unify two lambda nodes (higher-order unification).
        
        Handles alpha-equivalence, beta-reduction, and eta-conversion for proper
        higher-order unification.
        
        Args:
            lambda1: The first lambda node
            lambda2: The second lambda node
            bindings: Current variable bindings
            errors: List of errors
            
        Returns:
            Updated bindings and errors
        """
        # Check if the number of bound variables match
        if len(lambda1.bound_variables) != len(lambda2.bound_variables):
            errors.append(Error(f"Bound variable count mismatch: {len(lambda1.bound_variables)} and {len(lambda2.bound_variables)}", lambda1, lambda2))
            return None, errors
        
        # Create fresh variables for alpha-conversion
        fresh_vars = []
        var_subst1 = {}
        var_subst2 = {}
        
        for i in range(len(lambda1.bound_variables)):
            var1 = lambda1.bound_variables[i]
            var2 = lambda2.bound_variables[i]
            
            # Create a fresh variable with the same type
            fresh_var_id = self._next_var_id
            self._next_var_id += 1
            fresh_var = VariableNode(f"?fresh_{fresh_var_id}", fresh_var_id, var1.type)
            fresh_vars.append(fresh_var)
            
            # Create substitutions for both lambdas
            var_subst1[var1] = fresh_var
            var_subst2[var2] = fresh_var
        
        # Apply alpha-conversion to the bodies
        alpha_body1 = lambda1.body.substitute(var_subst1)
        alpha_body2 = lambda2.body.substitute(var_subst2)
        
        # Perform beta-reduction if needed (simplified)
        # In a full implementation, we would need to handle more complex cases
        beta_body1 = self._beta_reduce(alpha_body1)
        beta_body2 = self._beta_reduce(alpha_body2)
        
        # Perform eta-conversion if needed (simplified)
        # In a full implementation, we would need to handle more complex cases
        eta_body1 = self._eta_convert(beta_body1)
        eta_body2 = self._eta_convert(beta_body2)
        
        # Unify the normalized bodies
        return self.unify(eta_body1, eta_body2, bindings, "HIGHER_ORDER")
    
    def _beta_reduce(self, node: AST_Node) -> AST_Node:
        """
        Perform beta-reduction on an AST node.
        
        Beta-reduction is the process of applying a lambda abstraction to an argument.
        For example, (λx. P(x))(a) reduces to P(a).
        
        Args:
            node: The AST node to beta-reduce
            
        Returns:
            The beta-reduced AST node
        """
        # Check if the node is an application of a lambda
        if isinstance(node, ApplicationNode) and isinstance(node.operator, LambdaNode):
            lambda_node = node.operator
            
            # Check if the number of arguments matches the number of bound variables
            if len(node.arguments) == len(lambda_node.bound_variables):
                # Create a substitution for the bound variables
                substitution = {}
                for i, var in enumerate(lambda_node.bound_variables):
                    substitution[var] = node.arguments[i]
                
                # Apply the substitution to the lambda body
                return lambda_node.body.substitute(substitution)
        
        # If not a beta-redex or if there's a mismatch, return the original node
        return node
    
    def _eta_convert(self, node: AST_Node) -> AST_Node:
        """
        Perform eta-conversion on an AST node.
        
        Eta-conversion is the process of converting between λx. f(x) and f,
        when x does not occur free in f.
        
        Args:
            node: The AST node to eta-convert
            
        Returns:
            The eta-converted AST node
        """
        # Check if the node is a lambda with a body that is an application
        if isinstance(node, LambdaNode) and isinstance(node.body, ApplicationNode):
            lambda_node = node
            app_node = lambda_node.body
            
            # Check if the application's arguments are exactly the bound variables
            # and in the same order
            if len(app_node.arguments) == len(lambda_node.bound_variables):
                all_match = True
                for i, arg in enumerate(app_node.arguments):
                    if not (isinstance(arg, VariableNode) and
                            arg.var_id == lambda_node.bound_variables[i].var_id):
                        all_match = False
                        break
                
                # If all arguments match and the operator doesn't contain the bound variables,
                # we can eta-reduce
                if all_match:
                    contains_bound_var = False
                    for var in lambda_node.bound_variables:
                        if app_node.operator.contains_variable(var):
                            contains_bound_var = True
                            break
                    
                    if not contains_bound_var:
                        return app_node.operator
        
        # If not an eta-redex, return the original node
        return node
    
    def _unify_definition(self, def1: DefinitionNode, def2: DefinitionNode,
                         bindings: Dict[int, AST_Node], mode: str,
                         errors: List[Error]) -> Tuple[Optional[Dict[int, AST_Node]], List[Error]]:
        """
        Unify two definition nodes.
        
        Args:
            def1: The first definition node
            def2: The second definition node
            bindings: Current variable bindings
            mode: The unification mode
            errors: List of errors
            
        Returns:
            Updated bindings and errors
        """
        # Check if the symbol names match
        if def1.defined_symbol_name != def2.defined_symbol_name:
            errors.append(Error(f"Definition symbol mismatch: {def1.defined_symbol_name} and {def2.defined_symbol_name}", def1, def2))
            return None, errors
        
        # Check if the symbol types are compatible
        if not self.type_system.is_subtype(def1.defined_symbol_type, def2.defined_symbol_type) and not self.type_system.is_subtype(def2.defined_symbol_type, def1.defined_symbol_type):
            errors.append(Error(f"Definition type mismatch: {def1.defined_symbol_type} and {def2.defined_symbol_type}", def1, def2))
            return None, errors
        
        # Unify the definition bodies
        return self.unify(def1.definition_body_ast, def2.definition_body_ast, bindings, mode)