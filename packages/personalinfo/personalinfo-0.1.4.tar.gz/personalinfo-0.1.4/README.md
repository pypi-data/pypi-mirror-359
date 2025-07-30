# personalinfo

A simple Python package for basic arithmetic operations: addition, subtraction, multiplication, and division.

## Features
- Easy-to-use functions for common math operations
- Clean and minimal API
- Well-tested and ready for integration

## Installation

```bash
pip install personalinfo
```

## Usage

```python
from personalinfo import add, subtract, multiply, divide

print(add(2, 3))        # 5
print(subtract(5, 2))   # 3
print(multiply(4, 6))   # 24
print(divide(8, 2))     # 4.0
```

## API Reference

- `add(a, b)` – Add two numbers
- `subtract(a, b)` – Subtract b from a
- `multiply(a, b)` – Multiply two numbers
- `divide(a, b)` – Divide a by b (raises `ValueError` if b is 0)

## License

This project is licensed under the MIT License.