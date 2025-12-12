
# -*- coding: utf-8 -*-
"""
secure_calculator.calculator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A secure, production-ready calculator library that safely evaluates
mathematical expressions from untrusted string inputs.
"""

import ast
import operator
import sys

# --- Constants (Requirement 3.4) ---
MAX_EXPRESSION_LENGTH: int = 1024
"""The maximum allowed length for an input expression string."""

MAX_RESULT_MAGNITUDE: float = sys.float_info.max
"""The maximum absolute value for a calculation result."""


# --- Custom Exceptions (Requirement 2.5) ---
class CalculatorError(Exception):
    """Base exception for all calculator-related errors."""
    pass


class InvalidExpressionError(CalculatorError):
    """Raised for malformed, disallowed, or unsafe expressions."""
    pass


class DivisionByZeroError(CalculatorError):
    """Raised for division by zero attempts."""
    pass


class CalculationError(CalculatorError):
    """Raised for mathematical errors like overflow or domain errors."""
    pass


# --- AST Visitor Implementation (Requirement 3.2, 3.3) ---
class _SafeExpressionEvaluator(ast.NodeVisitor):
    """
    An AST node visitor that safely evaluates a whitelisted subset of nodes.
    This class is an internal implementation detail and not part of the public API.
    """
    # Whitelist of allowed AST node types
    _ALLOWED_NODE_TYPES = {
        ast.Expression,
        ast.Constant,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
    }

    # Whitelist of supported binary operations
    _BINARY_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
    }

    # Whitelist of supported unary operations
    _UNARY_OPERATORS = {
        ast.USub: operator.neg,
    }

    def visit(self, node: ast.AST) -> int | float:
        """
        Visit a node, ensuring it's on the whitelist before processing.
        This overrides the default `visit` to enforce security.
        """
        node_type = type(node)
        if node_type not in self._ALLOWED_NODE_TYPES:
            raise InvalidExpressionError(
                f"Disallowed expression element: {node_type.__name__}"
            )
        return super().visit(node)

    def visit_Expression(self, node: ast.Expression) -> int | float:
        """Evaluates the body of an expression."""
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> int | float:
        """Returns the value of a constant if it's a number."""
        value = node.value
        if not isinstance(value, (int, float)):
            raise InvalidExpressionError(
                f"Unsupported constant type: {type(value).__name__}"
            )
        return value

    def visit_BinOp(self, node: ast.BinOp) -> int | float:
        """Performs a binary operation."""
        op_type = type(node.op)
        operation = self._BINARY_OPERATORS.get(op_type)
        if operation is None:
            # This check is redundant due to the main visit method's whitelist,
            # but serves as a defense-in-depth measure.
            raise InvalidExpressionError(f"Unsupported operator: {op_type.__name__}")

        left_val = self.visit(node.left)
        right_val = self.visit(node.right)

        try:
            result = operation(left_val, right_val)
        except ZeroDivisionError:
            raise DivisionByZeroError("Division by zero is not allowed.")
        except (OverflowError, ValueError) as e:
            # ValueError can be raised by pow, e.g., pow(-1, 0.5)
            raise CalculationError(f"Mathematical domain error: {e}")

        # Post-operation check for magnitude (Requirement 3.4)
        if abs(result) > MAX_RESULT_MAGNITUDE:
            raise CalculationError("Calculation result exceeds the maximum allowed magnitude.")

        return result

    def visit_UnaryOp(self, node: ast.UnaryOp) -> int | float:
        """Performs a unary operation."""
        op_type = type(node.op)
        operation = self._UNARY_OPERATORS.get(op_type)
        if operation is None:
            raise InvalidExpressionError(f"Unsupported unary operator: {op_type.__name__}")

        operand_val = self.visit(node.operand)

        try:
            result = operation(operand_val)
        except OverflowError as e:
            raise CalculationError(f"Mathematical overflow during operation: {e}")

        if abs(result) > MAX_RESULT_MAGNITUDE:
            raise CalculationError("Calculation result exceeds the maximum allowed magnitude.")

        return result

    def generic_visit(self, node: ast.AST) -> None:
        """
        This method is called for nodes without a specific visit_ method.
        By raising an error here, we ensure that any node not explicitly
        whitelisted (even if its type is in _ALLOWED_NODE_TYPES) cannot be processed.
        This prevents accidental processing of valid but unhandled grammar.
        """
        raise InvalidExpressionError(
            f"Unsupported expression structure: {type(node).__name__}"
        )


# --- Public API (Requirement 4.1) ---
def calculate(expression: str) -> int | float:
    """
    Safely evaluates a mathematical expression.

    This function parses a string expression into an Abstract Syntax Tree (AST)
    and evaluates it using a secure visitor that only allows a whitelisted
    set of mathematical operations. It is designed to prevent arbitrary code
    execution vulnerabilities common with `eval()`.

    Args:
        expression: The string containing the mathematical expression.

    Returns:
        The result of the calculation as an integer or float.

    Raises:
        InvalidExpressionError: If the expression is syntactically invalid,
                                contains disallowed elements (e.g., function calls,
                                variables), or is too long.
        DivisionByZeroError: If the expression attempts to divide by zero.
        CalculationError: For other mathematical errors like overflow or
                          domain errors (e.g., negative number to a
                          fractional power).
        TypeError: If the provided expression is not a string.
    """
    # Input Sanitization and Validation (Requirement 3.4)
    if not isinstance(expression, str):
        raise TypeError("Expression must be a string.")

    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise InvalidExpressionError(
            f"Expression exceeds maximum length of {MAX_EXPRESSION_LENGTH} characters."
        )

    if not expression.strip():
        raise InvalidExpressionError("Expression cannot be empty.")

    # Parsing and Evaluation (Requirement 3.2)
    try:
        # 'eval' mode ensures the input is a single, valid expression.
        parsed_ast = ast.parse(expression, mode='eval')
    except SyntaxError as e:
        raise InvalidExpressionError(f"Invalid syntax: {e}") from e
    except (ValueError, TypeError) as e:
        # Catch other potential parsing errors, e.g., null bytes in string
        raise InvalidExpressionError(f"Failed to parse expression: {e}") from e

    evaluator = _SafeExpressionEvaluator()
    return evaluator.visit(parsed_ast)
