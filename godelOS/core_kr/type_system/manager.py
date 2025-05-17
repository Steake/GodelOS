"""
Type System Manager implementation.

This module defines the TypeSystemManager class, which is responsible for
managing the type hierarchy, type signatures, and type checking/inference.
"""

from typing import Dict, List, Optional, Set, Tuple
import networkx as nx

from godelOS.core_kr.ast.nodes import AST_Node
from godelOS.core_kr.type_system.types import (
    Type, AtomicType, FunctionType, TypeVariable,
    ParametricTypeConstructor, InstantiatedParametricType
)
from godelOS.core_kr.type_system.environment import TypeEnvironment
from godelOS.core_kr.type_system.visitor import (
    Error, TypeInferenceVisitor, TypeCheckingVisitor
)


class TypeSystemManager:
    """
    Manages the type hierarchy, type signatures, and type checking/inference.
    """
    
    def __init__(self):
        """Initialize the type system manager with base types and hierarchy."""
        # Type registry: name -> Type
        self._types: Dict[str, Type] = {}
        
        # Type hierarchy graph: nodes are AtomicType or InstantiatedParametricType,
        # edges represent subtyping (is_a)
        self._type_hierarchy = nx.DiGraph()
        
        # Signature table: symbol_name -> FunctionType or AtomicType
        self._signatures: Dict[str, Type] = {}
        
        # Initialize with base types
        self._initialize_base_types()
    
    def _initialize_base_types(self) -> None:
        """Initialize the base types and their hierarchy."""
        # Create base types
        entity_type = self.define_atomic_type("Entity")
        agent_type = self.define_atomic_type("Agent", ["Entity"])
        event_type = self.define_atomic_type("Event")
        action_type = self.define_atomic_type("Action", ["Event"])
        proposition_type = self.define_atomic_type("Proposition")
        
        # Primitive types
        boolean_type = self.define_atomic_type("Boolean")
        integer_type = self.define_atomic_type("Integer")
        string_type = self.define_atomic_type("String")
    
    def define_atomic_type(self, type_name: str, supertypes: Optional[List[str]] = None) -> AtomicType:
        """
        Define a new atomic type.
        
        Args:
            type_name: The name of the type
            supertypes: Optional list of supertype names
            
        Returns:
            The newly defined atomic type
        """
        if type_name in self._types:
            raise ValueError(f"Type {type_name} already defined")
        
        atomic_type = AtomicType(type_name)
        self._types[type_name] = atomic_type
        self._type_hierarchy.add_node(atomic_type)
        
        # Add edges for subtyping relationships
        if supertypes:
            for supertype_name in supertypes:
                if supertype_name not in self._types:
                    raise ValueError(f"Supertype {supertype_name} not defined")
                
                supertype = self._types[supertype_name]
                if not isinstance(supertype, AtomicType):
                    raise ValueError(f"Supertype {supertype_name} is not an atomic type")
                
                self._type_hierarchy.add_edge(atomic_type, supertype)
        
        return atomic_type
    
    def define_function_signature(self, symbol_name: str, arg_types_names: List[str], 
                                 return_type_name: str) -> None:
        """
        Define a function signature.
        
        Args:
            symbol_name: The name of the symbol
            arg_types_names: The names of the argument types
            return_type_name: The name of the return type
        """
        if symbol_name in self._signatures:
            raise ValueError(f"Symbol {symbol_name} already has a signature")
        
        arg_types = []
        for arg_type_name in arg_types_names:
            if arg_type_name not in self._types:
                raise ValueError(f"Type {arg_type_name} not defined")
            arg_types.append(self._types[arg_type_name])
        
        if return_type_name not in self._types:
            raise ValueError(f"Type {return_type_name} not defined")
        return_type = self._types[return_type_name]
        
        function_type = FunctionType(arg_types, return_type)
        self._signatures[symbol_name] = function_type
    
    def get_type(self, type_name: str) -> Optional[Type]:
        """
        Get a type by name.
        
        Args:
            type_name: The name of the type
            
        Returns:
            The type, or None if not found
        """
        return self._types.get(type_name)
    
    def is_subtype(self, subtype: Type, supertype: Type) -> bool:
        """
        Check if a type is a subtype of another type.
        
        Args:
            subtype: The potential subtype
            supertype: The potential supertype
            
        Returns:
            True if subtype is a subtype of supertype, False otherwise
        """
        if subtype == supertype:
            return True
        
        if isinstance(subtype, AtomicType) and isinstance(supertype, AtomicType):
            # Check if there's a path in the type hierarchy graph
            return nx.has_path(self._type_hierarchy, subtype, supertype)
        
        # For other type combinations, delegate to the is_subtype_of method
        return subtype.is_subtype_of(supertype, self)
    
    def check_expression_type(self, ast_node: AST_Node, expected_type: Type,
                              environment: TypeEnvironment) -> List[Error]:
        """
        Check if an expression has the expected type.
        
        Args:
            ast_node: The AST node representing the expression
            expected_type: The expected type
            environment: The type environment
            
        Returns:
            A list of errors, empty if the expression has the expected type
        """
        # Use the type checking visitor to check the expression type
        visitor = TypeCheckingVisitor(self, environment, expected_type)
        return ast_node.accept(visitor)
    
    def infer_expression_type(self, ast_node: AST_Node,
                              environment: TypeEnvironment) -> Tuple[Optional[Type], List[Error]]:
        """
        Infer the type of an expression.
        
        Args:
            ast_node: The AST node representing the expression
            environment: The type environment
            
        Returns:
            The inferred type and a list of errors
        """
        # Use the type inference visitor to infer the expression type
        visitor = TypeInferenceVisitor(self, environment)
        return ast_node.accept(visitor)
    
    def unify_types(self, type1: Type, type2: Type) -> Optional[Dict[TypeVariable, Type]]:
        """
        Unify two types, producing a substitution that makes them equal.
        
        Args:
            type1: The first type
            type2: The second type
            
        Returns:
            A substitution mapping type variables to types, or None if unification fails
        """
        # Handle the case where the types are already equal
        if type1 == type2:
            return {}
        
        # Handle the case where one is a type variable
        if isinstance(type1, TypeVariable):
            # Occurs check: ensure the variable doesn't appear in the other type
            # to prevent infinite types
            if self._occurs_check(type1, type2):
                return None
            return {type1: type2}
        
        if isinstance(type2, TypeVariable):
            # Occurs check
            if self._occurs_check(type2, type1):
                return None
            return {type2: type1}
        
        # Handle function types
        if isinstance(type1, FunctionType) and isinstance(type2, FunctionType):
            if len(type1.arg_types) != len(type2.arg_types):
                return None
            
            substitution = {}
            
            # Unify return types
            return_subst = self.unify_types(type1.return_type, type2.return_type)
            if return_subst is None:
                return None
            
            substitution.update(return_subst)
            
            # Unify argument types
            for arg1, arg2 in zip(type1.arg_types, type2.arg_types):
                # Apply current substitution to the types
                arg1_subst = arg1.substitute_type_vars(substitution)
                arg2_subst = arg2.substitute_type_vars(substitution)
                
                arg_subst = self.unify_types(arg1_subst, arg2_subst)
                if arg_subst is None:
                    return None
                
                # Update the substitution
                substitution.update(arg_subst)
                
                # Apply the new substitution to the existing bindings
                for var, type_obj in list(substitution.items()):
                    substitution[var] = type_obj.substitute_type_vars(arg_subst)
            
            return substitution
        
        # Handle parametric types
        if (isinstance(type1, InstantiatedParametricType) and
            isinstance(type2, InstantiatedParametricType)):
            if type1.constructor != type2.constructor:
                return None
            
            if len(type1.actual_type_args) != len(type2.actual_type_args):
                return None
            
            substitution = {}
            
            for arg1, arg2 in zip(type1.actual_type_args, type2.actual_type_args):
                # Apply current substitution to the types
                arg1_subst = arg1.substitute_type_vars(substitution)
                arg2_subst = arg2.substitute_type_vars(substitution)
                
                arg_subst = self.unify_types(arg1_subst, arg2_subst)
                if arg_subst is None:
                    return None
                
                # Update the substitution
                substitution.update(arg_subst)
                
                # Apply the new substitution to the existing bindings
                for var, type_obj in list(substitution.items()):
                    substitution[var] = type_obj.substitute_type_vars(arg_subst)
            
            return substitution
        
        # If we get here, unification failed
        return None
        
    def _occurs_check(self, var: TypeVariable, type_obj: Type) -> bool:
        """
        Check if a type variable occurs in a type.
        
        Args:
            var: The type variable to check for
            type_obj: The type to check in
            
        Returns:
            True if the variable occurs in the type, False otherwise
        """
        if var == type_obj:
            return True
            
        if isinstance(type_obj, FunctionType):
            return (any(self._occurs_check(var, arg_type) for arg_type in type_obj.arg_types) or
                   self._occurs_check(var, type_obj.return_type))
                   
        if isinstance(type_obj, InstantiatedParametricType):
            return any(self._occurs_check(var, arg_type) for arg_type in type_obj.actual_type_args)
            
        return False