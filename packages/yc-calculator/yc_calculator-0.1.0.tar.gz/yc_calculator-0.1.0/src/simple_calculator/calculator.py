"""Calculator module providing basic arithmetic operations."""

import numpy as np
from typing import Union, List


class Calculator:
    """A simple calculator class with basic arithmetic operations."""

    def __init__(self):
        """Initialize the calculator."""
        pass

    def add(self, a: Union[int, float, List], b: Union[int, float, List]) -> Union[int, float, np.ndarray]:
        """Add two numbers or arrays."""
        if isinstance(a, (list, np.ndarray)) or isinstance(b, (list, np.ndarray)):
            return np.add(a, b)
        return a + b

    def subtract(self, a: Union[int, float, List], b: Union[int, float, List]) -> Union[int, float, np.ndarray]:
        """Subtract two numbers or arrays."""
        if isinstance(a, (list, np.ndarray)) or isinstance(b, (list, np.ndarray)):
            return np.subtract(a, b)
        return a - b

    def multiply(self, a: Union[int, float, List], b: Union[int, float, List]) -> Union[int, float, np.ndarray]:
        """Multiply two numbers or arrays."""
        if isinstance(a, (list, np.ndarray)) or isinstance(b, (list, np.ndarray)):
            return np.multiply(a, b)
        return a * b

    def divide(self, a: Union[int, float, List], b: Union[int, float, List]) -> Union[int, float, np.ndarray]:
        """Divide two numbers or arrays."""
        if isinstance(a, (list, np.ndarray)) or isinstance(b, (list, np.ndarray)):
            return np.divide(a, b)
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b

    def power(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Raise a to the power of b."""
        return a ** b

    def sqrt(self, a: Union[int, float]) -> float:
        """Calculate the square root of a number."""
        if a < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return np.sqrt(a) 