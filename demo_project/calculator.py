"""Calculator module — demo project for agent testing.

Contains an intentional bug in the divide function.
"""


def add(a: float, b: float) -> float:
    """Return the sum of a and b."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the difference of a and b."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of a and b."""
    return a * b


def divide(a: float, b: float) -> float:
    """Return the quotient of a divided by b.

    BUG: This currently multiplies instead of dividing!
    """
    return a / b  # ← BUG: should be a / b


def calculate_total(numbers: list[float]) -> float:
    """Calculate the total of a list of numbers.

    BUG: 'total' is not defined before being used.
    """
    return total
