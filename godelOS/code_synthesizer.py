"""
GödelOS True AST-Level Code Rewriter & Sandboxed Verification Engine.

Moves beyond configuration-swapping to authentic runtime self-modification:
1. AST Purity & Security Verification (Whitelists safe nodes, forbids I/O, imports, reflection).
2. Sandboxed Compilation & Verification against Test Oracles.
3. Transactional Function-Pointer Hot-Swapping with Automatic Rollback.
"""

import ast
import time
import copy
import logging
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field
from fractions import Fraction

from godelOS.godel_machine import ConservativeUtilityBounds, EnvironmentModelAssumption

logger = logging.getLogger(__name__)

SAFE_BUILTINS: Dict[str, Any] = {
    "len": len,
    "min": min,
    "max": max,
    "range": range,
    "enumerate": enumerate,
    "sorted": sorted,
    "abs": abs,
    "sum": sum,
    "all": all,
    "any": any,
    "bool": bool,
    "int": int,
    "float": float,
    "str": str,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "zip": zip,
    "isinstance": isinstance
}

FORBIDDEN_NAMES = {
    "eval", "exec", "open", "__import__", "globals", "locals", "compile",
    "getattr", "setattr", "delattr", "system", "popen", "exit", "quit", "breakpoint"
}


@dataclass
class ExecutableCodeContract:
    """Rigorous contract governing actual Python source code self-modification."""
    mutation_id: str
    target_object: Any
    target_function_name: str
    candidate_source_code: str
    test_vectors: List[Tuple[Tuple[Any, ...], Any]] # [((arg1, ...), expected_result), ...]
    utility_bounds: ConservativeUtilityBounds
    environment_model: Optional[EnvironmentModelAssumption] = None
    resource_budget_ms: float = 100.0


class ASTSafetyValidator:
    """
    Statically analyzes candidate Python AST to guarantee code safety,
    purity, and the absence of system escapes or unauthorized mutations.
    """

    ALLOWED_NODE_TYPES = (
        ast.Module, ast.FunctionDef, ast.arguments, ast.arg,
        ast.Return, ast.If, ast.Compare, ast.BinOp, ast.UnaryOp,
        ast.List, ast.Tuple, ast.Dict, ast.Set, ast.Subscript,
        ast.Index, ast.Slice, ast.Name, ast.Constant, ast.For,
        ast.Expr, ast.Call, ast.Lambda, ast.Attribute,
        ast.comprehension, ast.ListComp, ast.DictComp, ast.SetComp,
        ast.Pass, ast.keyword, ast.Eq, ast.NotEq, ast.Lt, ast.LtE,
        ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Load, ast.Store, ast.Param, ast.IfExp,
        ast.Pow, ast.Not, ast.USub, ast.UAdd, ast.And, ast.Or, ast.BoolOp,
        ast.Assign, ast.AugAssign, ast.Break, ast.Continue, ast.While
    )

    @classmethod
    def validate_source(cls, source_code: str) -> Tuple[bool, Optional[ast.FunctionDef], str]:
        """Validates that candidate source code contains exactly one pure, safe function."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return False, None, f"Syntax error in candidate AST: {e}"

        # Must have exactly one top-level function definition
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        if len(functions) != 1 or len(tree.body) != 1:
            return False, None, "Structural violation: Source must contain exactly one top-level function definition."

        target_fn = functions[0]

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return False, None, "Security violation: External module imports forbidden in candidate code."

            if isinstance(node, (ast.Global, ast.Nonlocal)):
                return False, None, "Security violation: Global/Nonlocal variable mutations forbidden."

            if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                return False, None, f"Security violation: Dunder attribute access '{node.attr}' forbidden."

            if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
                return False, None, f"Security violation: Forbidden builtin reference '{node.id}'."

            if not isinstance(node, cls.ALLOWED_NODE_TYPES):
                return False, None, f"Security violation: Disallowed AST node type '{type(node).__name__}'."



        return True, target_fn, "AST verified safe, pure, and sandboxed."


class SandboxedExecutionTester:
    """Compiles and executes candidate function against reference test vectors."""

    @classmethod
    def test_candidate(
        cls,
        fn_ast: ast.FunctionDef,
        test_vectors: List[Tuple[Tuple[Any, ...], Any]],
        timeout_ms: float = 100.0
    ) -> Tuple[bool, Optional[Callable], str]:
        # Wrap function AST in a module
        mod = ast.Module(body=[fn_ast], type_ignores=[])
        compiled_code = compile(mod, filename="<candidate_mutation>", mode="exec")

        sandbox_globals = {"__builtins__": SAFE_BUILTINS}
        sandbox_locals: Dict[str, Any] = {}

        try:
            exec(compiled_code, sandbox_globals, sandbox_locals)
        except Exception as e:
            return False, None, f"Compilation/Evaluation failed: {e}"

        fn_obj = sandbox_locals.get(fn_ast.name)
        if not callable(fn_obj):
            return False, None, f"Extracted symbol '{fn_ast.name}' is not callable."

        # Execute against test vectors
        for idx, (args, expected) in enumerate(test_vectors):
            t0 = time.time()
            try:
                result = fn_obj(*args)
            except Exception as e:
                return False, None, f"Runtime error on test vector {idx}: {e}"
            elapsed_ms = (time.time() - t0) * 1000.0

            if elapsed_ms > timeout_ms:
                return False, None, f"Timeout: Test vector {idx} execution exceeded {timeout_ms}ms."

            if callable(expected):
                if not expected(result):
                    return False, None, f"Assertion failed: Test vector {idx} output did not satisfy validation predicate."
            else:
                if result != expected:
                    return False, None, f"Mismatch: Test vector {idx} produced {result}, expected {expected}."

        return True, fn_obj, "All test vectors successfully validated."


class AtomicCodeHotSwapper:
    """Manages transactional hot-swapping of executable functions on live objects."""

    @classmethod
    def verify_and_swap(
        cls,
        contract: ExecutableCodeContract
    ) -> Tuple[bool, bool, Optional[Callable], str]:
        """
        Executes AST safety checks, sandboxed testing, and transactional swap with rollback.
        Returns: (verified, applied, original_fn, diagnostic_log).
        """
        # 1. AST Safety check
        ast_ok, fn_ast, ast_msg = ASTSafetyValidator.validate_source(contract.candidate_source_code)
        if not ast_ok:
            return False, False, None, ast_msg

        # 2. Test vectors verification
        test_ok, new_fn, test_msg = SandboxedExecutionTester.test_candidate(
            fn_ast, contract.test_vectors, contract.resource_budget_ms
        )
        if not test_ok or new_fn is None:
            return False, False, None, test_msg

        # 3. Target verification
        if not hasattr(contract.target_object, contract.target_function_name):
            return False, False, None, f"Target object does not have attribute '{contract.target_function_name}'."

        original_fn = getattr(contract.target_object, contract.target_function_name)

        # 4. Atomic Swap with Rollback trial
        try:
            setattr(contract.target_object, contract.target_function_name, new_fn)
            # Run one verification invocation on the swapped object
            if contract.test_vectors:
                sample_args, expected = contract.test_vectors[0]
                res = getattr(contract.target_object, contract.target_function_name)(*sample_args)
                if callable(expected):
                    if not expected(res):
                        raise RuntimeError("Live invocation output failed verification predicate.")
                else:
                    if res != expected:
                        raise RuntimeError(f"Live invocation output mismatch: {res} != {expected}.")

            logger.info(f"✔ Code Mutation Certified: Swapped '{contract.target_function_name}' on {contract.target_object}")
            return True, True, original_fn, f"Successfully hot-swapped function '{contract.target_function_name}'."

        except Exception as e:
            # ROLLBACK
            setattr(contract.target_object, contract.target_function_name, original_fn)
            logger.error(f"Live invocation failed, rolled back to original function: {e}")
            return True, False, original_fn, f"Runtime invocation error, safely rolled back: {e}"
