# Simple Calculator

A simple calculator package for learning Python packaging with setuptools and pyproject.toml.

## Installation

```bash
pip install simple-calculator
```

## Usage

### As a Python module

```python
from simple_calculator import Calculator

calc = Calculator()
result = calc.add(5, 3)  # Returns 8
result = calc.multiply(4, 7)  # Returns 28
```

### As a command-line tool

```bash
calc add 5 3
calc multiply 4 7
calc sqrt 16
```

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Format code:

```bash
black src/ tests/
```

## License

MIT License 