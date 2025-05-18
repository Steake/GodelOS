"""
Formal Logic Parser implementation.

This module implements the FormalLogicParser class, which is responsible for
converting textual representations of logical formulae into canonical
Abstract Syntax Tree (AST) structures.
"""

from typing import Dict, List, Optional, Tuple, Union
import re

from godelOS.core_kr.ast.nodes import (
    AST_Node, ConstantNode, VariableNode, ApplicationNode,
    QuantifierNode, ConnectiveNode, ModalOpNode, LambdaNode
)
from godelOS.core_kr.type_system.manager import TypeSystemManager
from godelOS.core_kr.type_system.types import Type, FunctionType


class Token:
    """A token in the input stream."""
    
    def __init__(self, type_: str, value: str, position: int):
        """
        Initialize a token.
        
        Args:
            type_: The type of the token
            value: The value of the token
            position: The position of the token in the input
        """
        self.type = type_
        self.value = value
        self.position = position
    
    def __str__(self) -> str:
        return f"{self.type}({self.value})"
    
    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value}, {self.position})"


class Lexer:
    """
    Lexical analyzer for the formal logic language.
    
    Converts an input string into a stream of tokens.
    """
    
    # Token types and their regex patterns
    TOKEN_SPECS = [
        ('WHITESPACE', r'\s+'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACKET', r'\['),
        ('RBRACKET', r'\]'),
        ('LBRACE', r'\{'),
        ('RBRACE', r'\}'),
        ('COMMA', r','),
        ('DOT', r'\.'),
        ('COLON', r':'),
        ('FORALL', r'forall|∀'),
        ('EXISTS', r'exists|∃'),
        ('LAMBDA', r'lambda|λ'),
        ('NOT', r'not|¬'),
        ('AND', r'and|∧'),
        ('OR', r'or|∨'),
        ('IMPLIES', r'implies|=>|⇒'),
        ('EQUIV', r'equiv|<=>|≡'),
        ('KNOWS', r'knows|K'),
        ('BELIEVES', r'believes|B'),
        ('POSSIBLE', r'possible|◇'),
        ('NECESSARY', r'necessary|□'),
        ('PROBABILITY', r'prob|P'),
        ('DEFEASIBLE', r'defeasibly|def'),
        ('TRUE', r'True|true|⊤'),
        ('FALSE', r'False|false|⊥'),
        ('VARIABLE', r'\?[a-zA-Z][a-zA-Z0-9_]*'),
        ('CONSTANT', r'[a-zA-Z][a-zA-Z0-9_]*'),
        ('NUMBER', r'-?\d+(\.\d+)?'),
        ('STRING', r'"[^"]*"'),
        ('UNKNOWN', r'.'),
    ]
    
    def __init__(self):
        """Initialize the lexer."""
        # Compile the regex patterns
        self.token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.TOKEN_SPECS)
        self.token_regex = re.compile(self.token_regex)
    
    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenize the input text.
        
        Args:
            text: The input text
            
        Returns:
            A list of tokens
        """
        tokens = []
        position = 0
        
        for match in self.token_regex.finditer(text):
            token_type = match.lastgroup
            token_value = match.group()
            
            if token_type == 'WHITESPACE':
                # Skip whitespace
                position = match.end()
                continue
            
            if token_type == 'UNKNOWN':
                # Unknown token, raise an error
                raise ValueError(f"Unknown token '{token_value}' at position {position}")
            
            tokens.append(Token(token_type, token_value, position))
            position = match.end()
        
        return tokens


class Error:
    """An error during parsing."""
    
    def __init__(self, message: str, position: int):
        """
        Initialize an error.
        
        Args:
            message: The error message
            position: The position in the input where the error occurred
        """
        self.message = message
        self.position = position
    
    def __str__(self) -> str:
        return f"{self.message} at position {self.position}"


class FormalLogicParser:
    """
    Parser for the formal logic language.
    
    Converts a textual representation of a logical formula into an AST.
    Supports higher-order logic (HOL) with extensions for modality, probability, and defeasibility.
    """
    
    def __init__(self, type_system: TypeSystemManager):
        """
        Initialize the parser.
        
        Args:
            type_system: The type system manager for type validation and inference
        """
        self.type_system = type_system
        self.lexer = Lexer()
        self.tokens: List[Token] = []
        self.current_token_index = 0
        self.errors: List[Error] = []
        self.var_counter = 0
        
        # Get common types from the type system
        self.entity_type = self.type_system.get_type("Entity")
        self.boolean_type = self.type_system.get_type("Boolean")
        self.proposition_type = self.type_system.get_type("Proposition")
        
        # Initialize variable environment for type checking during parsing
        self.variable_types: Dict[str, 'Type'] = {}
    
    def parse(self, expression_string: str) -> Tuple[Optional[AST_Node], List[Error]]:
        """
        Parse a logical expression.
        
        Args:
            expression_string: The expression to parse
            
        Returns:
            The AST node representing the expression, or None if parsing failed,
            and a list of errors
        """
        self.tokens = self.lexer.tokenize(expression_string)
        self.current_token_index = 0
        self.errors = []
        self.var_counter = 0
        
        if not self.tokens:
            self.errors.append(Error("Empty expression", 0))
            return None, self.errors
        
        try:
            ast = self.parse_expression()
            
            # Check if we've consumed all tokens
            if self.current_token_index < len(self.tokens):
                self.errors.append(Error(
                    f"Unexpected token '{self.tokens[self.current_token_index].value}'",
                    self.tokens[self.current_token_index].position
                ))
                return None, self.errors
            
            return ast, self.errors
        except Exception as e:
            self.errors.append(Error(str(e), self.tokens[self.current_token_index].position if self.current_token_index < len(self.tokens) else 0))
            return None, self.errors
    
    def current_token(self) -> Optional[Token]:
        """
        Get the current token.
        
        Returns:
            The current token, or None if at the end of the token stream
        """
        if self.current_token_index >= len(self.tokens):
            return None
        return self.tokens[self.current_token_index]
    
    def consume_token(self) -> Optional[Token]:
        """
        Consume the current token and advance to the next one.
        
        Returns:
            The consumed token, or None if at the end of the token stream
        """
        token = self.current_token()
        self.current_token_index += 1
        return token
    
    def expect_token(self, expected_type: str) -> Token:
        """
        Expect a token of a certain type.
        
        Args:
            expected_type: The expected token type
            
        Returns:
            The token if it matches the expected type
            
        Raises:
            ValueError: If the token doesn't match the expected type
        """
        token = self.current_token()
        if not token:
            raise ValueError(f"Expected {expected_type}, got end of input")
        
        if token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token.type}({token.value})")
        
        self.consume_token()
        return token
    
    def parse_expression(self) -> AST_Node:
        """
        Parse an expression.
        
        Returns:
            The AST node representing the expression
        """
        return self.parse_logical_expression()
    
    def parse_logical_expression(self) -> AST_Node:
        """
        Parse a logical expression (top-level).
        
        This handles binary connectives (AND, OR, IMPLIES, EQUIV) with appropriate precedence.
        
        Returns:
            The AST node representing the logical expression
        """
        # Parse the left-hand side
        expr = self.parse_unary_expression()
        
        # Parse binary connectives if present
        while self.current_token() and self.current_token().type in ('AND', 'OR', 'IMPLIES', 'EQUIV'):
            connective_type = self.current_token().type
            self.consume_token()
            
            # Parse the right-hand side
            right = self.parse_unary_expression()
            
            # Create a connective node
            expr = ConnectiveNode(connective_type, [expr, right], self.proposition_type)
        
        return expr
    
    def parse_unary_expression(self) -> AST_Node:
        """
        Parse a unary expression.
        
        This handles unary operators (NOT, KNOWS, BELIEVES, etc.).
        
        Returns:
            The AST node representing the unary expression
        """
        token = self.current_token()
        if not token:
            raise ValueError("Unexpected end of input")
        
        if token.type == 'NOT':
            # Negation
            self.consume_token()
            expr = self.parse_unary_expression()
            return ConnectiveNode('NOT', [expr], self.proposition_type)
        
        if token.type in ('KNOWS', 'BELIEVES', 'POSSIBLE', 'NECESSARY'):
            # Modal operator
            modal_op = token.type
            self.consume_token()
            
            # Parse the agent or world (optional)
            agent_or_world = None
            if self.current_token() and self.current_token().type == 'LBRACKET':
                self.consume_token()
                agent_or_world = self.parse_expression()
                self.expect_token('RBRACKET')
            
            # Parse the proposition
            proposition = self.parse_unary_expression()
            
            return ModalOpNode(modal_op, proposition, self.proposition_type, agent_or_world)
        
        if token.type == 'PROBABILITY':
            # Probability operator
            self.consume_token()
            
            # Parse the probability value if present
            prob_value = None
            if self.current_token() and self.current_token().type == 'LBRACKET':
                self.consume_token()
                if self.current_token() and self.current_token().type == 'NUMBER':
                    prob_value = float(self.consume_token().value)
                else:
                    raise ValueError("Expected probability value after P[")
                self.expect_token('RBRACKET')
            
            # Parse the proposition
            proposition = self.parse_unary_expression()
            
            # Create a modal operator node for probability
            metadata = {"probability": prob_value} if prob_value is not None else {}
            return ModalOpNode('PROBABILITY', proposition, self.proposition_type, None, metadata)
        
        if token.type == 'DEFEASIBLE':
            # Defeasible operator
            self.consume_token()
            
            # Parse the proposition
            proposition = self.parse_unary_expression()
            
            # Create a modal operator node for defeasibility
            return ModalOpNode('DEFEASIBLE', proposition, self.proposition_type)
        
        return self.parse_quantifier_expression()
    
    def parse_quantifier_expression(self) -> AST_Node:
        """
        Parse a quantifier expression.
        
        This handles universal and existential quantifiers (FORALL, EXISTS).
        
        Returns:
            The AST node representing the quantifier expression
        """
        token = self.current_token()
        if not token:
            raise ValueError("Unexpected end of input")
        
        if token.type in ('FORALL', 'EXISTS'):
            # Quantifier
            quantifier_type = token.type
            self.consume_token()
            
            # Parse the bound variables with optional type annotations
            bound_vars = []
            var_types = {}  # Store variable types for scope
            
            while self.current_token() and self.current_token().type == 'VARIABLE':
                var_token = self.consume_token()
                var_name = var_token.value
                var_id = self.var_counter
                self.var_counter += 1
                
                # Check for type annotation
                var_type = self.entity_type  # Default type
                if self.current_token() and self.current_token().type == 'COLON':
                    self.consume_token()
                    if self.current_token() and self.current_token().type == 'CONSTANT':
                        type_name = self.consume_token().value
                        var_type = self.type_system.get_type(type_name)
                        if not var_type:
                            self.errors.append(Error(f"Unknown type '{type_name}'", var_token.position))
                            var_type = self.entity_type  # Fallback to default
                    else:
                        raise ValueError("Expected type name after colon")
                
                var_node = VariableNode(var_name, var_id, var_type)
                bound_vars.append(var_node)
                var_types[var_name] = var_type
            
            if not bound_vars:
                raise ValueError(f"Expected at least one variable after {quantifier_type}")
            
            # Save current variable environment
            old_var_types = self.variable_types.copy()
            
            # Add bound variables to environment for scope
            self.variable_types.update(var_types)
            
            # Parse the scope
            self.expect_token('DOT')
            scope = self.parse_expression()
            
            # Restore variable environment
            self.variable_types = old_var_types
            
            return QuantifierNode(quantifier_type, bound_vars, scope, self.proposition_type)
        
        return self.parse_lambda_expression()
    
    def parse_lambda_expression(self) -> AST_Node:
        """
        Parse a lambda expression.
        
        This handles lambda abstractions (lambda ?x. body).
        
        Returns:
            The AST node representing the lambda expression
        """
        token = self.current_token()
        if not token:
            raise ValueError("Unexpected end of input")
        
        if token.type == 'LAMBDA':
            # Lambda abstraction
            self.consume_token()
            
            # Parse the bound variables with optional type annotations
            bound_vars = []
            var_types = {}  # Store variable types for body
            
            while self.current_token() and self.current_token().type == 'VARIABLE':
                var_token = self.consume_token()
                var_name = var_token.value
                var_id = self.var_counter
                self.var_counter += 1
                
                # Check for type annotation
                var_type = self.entity_type  # Default type
                if self.current_token() and self.current_token().type == 'COLON':
                    self.consume_token()
                    if self.current_token() and self.current_token().type == 'CONSTANT':
                        type_name = self.consume_token().value
                        var_type = self.type_system.get_type(type_name)
                        if not var_type:
                            self.errors.append(Error(f"Unknown type '{type_name}'", var_token.position))
                            var_type = self.entity_type  # Fallback to default
                    else:
                        raise ValueError("Expected type name after colon")
                
                var_node = VariableNode(var_name, var_id, var_type)
                bound_vars.append(var_node)
                var_types[var_name] = var_type
            
            if not bound_vars:
                raise ValueError("Expected at least one variable after lambda")
            
            # Save current variable environment
            old_var_types = self.variable_types.copy()
            
            # Add bound variables to environment for body
            self.variable_types.update(var_types)
            
            # Parse the body
            self.expect_token('DOT')
            body = self.parse_expression()
            
            # Restore variable environment
            self.variable_types = old_var_types
            
            # Infer the lambda type based on bound variables and body
            arg_types = [var.type for var in bound_vars]
            return_type = body.type
            lambda_type = self.type_system.get_type("Entity")  # Default fallback
            
            # Try to create a function type
            try:
                lambda_type = FunctionType(arg_types, return_type)
            except Exception as e:
                self.errors.append(Error(f"Error creating lambda type: {str(e)}", token.position))
            
            return LambdaNode(bound_vars, body, lambda_type)
        
        return self.parse_application_expression()
    
    def parse_application_expression(self) -> AST_Node:
        """
        Parse a function or predicate application.
        
        This handles function applications like Pred(arg1, arg2).
        
        Returns:
            The AST node representing the application
        """
        # Parse the primary expression (which could be the operator)
        expr = self.parse_primary_expression()
        
        # Check if it's followed by an argument list
        if self.current_token() and self.current_token().type == 'LPAREN':
            self.consume_token()
            
            # Parse the arguments
            arguments = []
            if self.current_token() and self.current_token().type != 'RPAREN':
                arguments.append(self.parse_expression())
                
                while self.current_token() and self.current_token().type == 'COMMA':
                    self.consume_token()
                    arguments.append(self.parse_expression())
            
            self.expect_token('RPAREN')
            
            # Infer the return type based on the operator and arguments
            return_type = self.boolean_type  # Default for predicates
            
            # If the operator is a function type, use its return type
            if hasattr(expr, 'type') and isinstance(expr.type, FunctionType):
                return_type = expr.type.return_type
            
            return ApplicationNode(expr, arguments, return_type)
        
        return expr
    
    def parse_primary_expression(self) -> AST_Node:
        """
        Parse a primary expression.
        
        This handles basic expressions like constants, variables, and parenthesized expressions.
        
        Returns:
            The AST node representing the primary expression
        """
        token = self.current_token()
        if not token:
            raise ValueError("Unexpected end of input")
        
        if token.type == 'LPAREN':
            # Parenthesized expression
            self.consume_token()
            expr = self.parse_expression()
            self.expect_token('RPAREN')
            return expr
        
        if token.type == 'VARIABLE':
            # Variable
            var_name = token.value
            position = token.position
            self.consume_token()
            
            # Check for type annotation
            var_type = self.variable_types.get(var_name, self.entity_type)  # Default or from environment
            if self.current_token() and self.current_token().type == 'COLON':
                self.consume_token()
                if self.current_token() and self.current_token().type == 'CONSTANT':
                    type_name = self.consume_token().value
                    annotated_type = self.type_system.get_type(type_name)
                    if annotated_type:
                        var_type = annotated_type
                    else:
                        self.errors.append(Error(f"Unknown type '{type_name}'", position))
                else:
                    raise ValueError("Expected type name after colon")
            
            var_id = self.var_counter
            self.var_counter += 1
            return VariableNode(var_name, var_id, var_type)
        
        if token.type == 'CONSTANT':
            # Constant
            const_name = token.value
            position = token.position
            self.consume_token()
            
            # Check for type annotation
            const_type = self.entity_type  # Default
            if self.current_token() and self.current_token().type == 'COLON':
                self.consume_token()
                if self.current_token() and self.current_token().type == 'CONSTANT':
                    type_name = self.consume_token().value
                    annotated_type = self.type_system.get_type(type_name)
                    if annotated_type:
                        const_type = annotated_type
                    else:
                        self.errors.append(Error(f"Unknown type '{type_name}'", position))
                else:
                    raise ValueError("Expected type name after colon")
            
            # Check if this is a known function/predicate
            if const_name in self.type_system._signatures:
                const_type = self.type_system._signatures[const_name]
            
            return ConstantNode(const_name, const_type)
        
        if token.type == 'NUMBER':
            # Numeric literal
            value = token.value
            self.consume_token()
            
            # Determine if it's an integer or float
            if '.' in value:
                num_value = float(value)
                num_type = self.type_system.get_type("Float") or self.type_system.get_type("Real") or self.entity_type
            else:
                num_value = int(value)
                num_type = self.type_system.get_type("Integer") or self.entity_type
            
            return ConstantNode(value, num_type, num_value)
        
        if token.type == 'STRING':
            # String literal
            value = token.value[1:-1]  # Remove quotes
            self.consume_token()
            string_type = self.type_system.get_type("String") or self.entity_type
            return ConstantNode(value, string_type, value)
        
        if token.type == 'TRUE':
            # Boolean true
            self.consume_token()
            return ConstantNode("True", self.boolean_type, True)
        
        if token.type == 'FALSE':
            # Boolean false
            self.consume_token()
            return ConstantNode("False", self.boolean_type, False)
        
        # If we get here, we don't know how to parse this token
        raise ValueError(f"Unexpected token '{token.value}' of type '{token.type}'")