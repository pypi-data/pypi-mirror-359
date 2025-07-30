"""Tests for the Calculator class."""

import pytest
import numpy as np
from simple_calculator import Calculator


class TestCalculator:
    """Test cases for Calculator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calc = Calculator()

    def test_add_integers(self):
        """Test addition of integers."""
        assert self.calc.add(5, 3) == 8
        assert self.calc.add(-1, 1) == 0
        assert self.calc.add(0, 0) == 0

    def test_add_floats(self):
        """Test addition of floats."""
        assert self.calc.add(5.5, 3.2) == 8.7
        assert self.calc.add(-1.5, 1.5) == 0.0

    def test_add_arrays(self):
        """Test addition of arrays."""
        a = [1, 2, 3]
        b = [4, 5, 6]
        result = self.calc.add(a, b)
        assert np.array_equal(result, np.array([5, 7, 9]))

    def test_subtract_integers(self):
        """Test subtraction of integers."""
        assert self.calc.subtract(5, 3) == 2
        assert self.calc.subtract(1, 1) == 0
        assert self.calc.subtract(0, 5) == -5

    def test_subtract_floats(self):
        """Test subtraction of floats."""
        assert self.calc.subtract(5.5, 3.2) == 2.3
        assert self.calc.subtract(1.5, 1.5) == 0.0

    def test_subtract_arrays(self):
        """Test subtraction of arrays."""
        a = [5, 7, 9]
        b = [1, 2, 3]
        result = self.calc.subtract(a, b)
        assert np.array_equal(result, np.array([4, 5, 6]))

    def test_multiply_integers(self):
        """Test multiplication of integers."""
        assert self.calc.multiply(5, 3) == 15
        assert self.calc.multiply(-2, 3) == -6
        assert self.calc.multiply(0, 5) == 0

    def test_multiply_floats(self):
        """Test multiplication of floats."""
        assert self.calc.multiply(2.5, 3.0) == 7.5
        assert self.calc.multiply(-1.5, 2.0) == -3.0

    def test_multiply_arrays(self):
        """Test multiplication of arrays."""
        a = [1, 2, 3]
        b = [4, 5, 6]
        result = self.calc.multiply(a, b)
        assert np.array_equal(result, np.array([4, 10, 18]))

    def test_divide_integers(self):
        """Test division of integers."""
        assert self.calc.divide(6, 2) == 3.0
        assert self.calc.divide(5, 2) == 2.5
        assert self.calc.divide(0, 5) == 0.0

    def test_divide_floats(self):
        """Test division of floats."""
        assert self.calc.divide(6.0, 2.0) == 3.0
        assert self.calc.divide(5.0, 2.0) == 2.5

    def test_divide_arrays(self):
        """Test division of arrays."""
        a = [6, 10, 18]
        b = [2, 5, 6]
        result = self.calc.divide(a, b)
        assert np.array_equal(result, np.array([3.0, 2.0, 3.0]))

    def test_divide_by_zero(self):
        """Test division by zero raises error."""
        with pytest.raises(ValueError, match="Division by zero is not allowed"):
            self.calc.divide(5, 0)

    def test_power(self):
        """Test power operation."""
        assert self.calc.power(2, 3) == 8
        assert self.calc.power(5, 0) == 1
        assert self.calc.power(2, -1) == 0.5

    def test_sqrt(self):
        """Test square root operation."""
        assert self.calc.sqrt(4) == 2.0
        assert self.calc.sqrt(9) == 3.0
        assert self.calc.sqrt(0) == 0.0

    def test_sqrt_negative(self):
        """Test square root of negative number raises error."""
        with pytest.raises(ValueError, match="Cannot calculate square root of negative number"):
            self.calc.sqrt(-1) 