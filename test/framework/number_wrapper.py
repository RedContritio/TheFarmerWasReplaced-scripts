import sys
import os

# Add parent directory to path to import utils modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils_math import sign as _sign, clamp as _clamp
from .tick_system import _add_ticks


class Number(float):
    """
    Number wrapper class that extends float with utility methods.
    This allows calling utility functions as methods on numeric values.
    """

    def __new__(cls, value):
        return float.__new__(cls, value)

    def sign(self):
        """Return the sign of the number: 1 for positive, -1 for negative, 0 for zero"""
        return Number(_sign(self))

    def clamp(self, min_value, max_value):
        """Clamp the value between min_value and max_value"""
        return Number(_clamp(self, min_value, max_value))

    # Ensure arithmetic operations return Number instances
    # Note: tick counting is handled by AST transformer, not here
    def __add__(self, other):
        print(
            f"[DEBUG Number.__add__] self={self}, other={other}, type(other)={type(other)}"
        )
        return Number(float.__add__(self, other))

    def __radd__(self, other):
        return Number(float.__radd__(self, other))

    def __sub__(self, other):
        return Number(float.__sub__(self, other))

    def __rsub__(self, other):
        return Number(float.__rsub__(self, other))

    def __mul__(self, other):
        return Number(float.__mul__(self, other))

    def __rmul__(self, other):
        return Number(float.__rmul__(self, other))

    def __truediv__(self, other):
        return Number(float.__truediv__(self, other))

    def __rtruediv__(self, other):
        return Number(float.__rtruediv__(self, other))

    def __floordiv__(self, other):
        return Number(float.__floordiv__(self, other))

    def __rfloordiv__(self, other):
        return Number(float.__rfloordiv__(self, other))

    def __mod__(self, other):
        return Number(float.__mod__(self, other))

    def __rmod__(self, other):
        return Number(float.__rmod__(self, other))

    def __pow__(self, other):
        return Number(float.__pow__(self, other))

    def __rpow__(self, other):
        return Number(float.__rpow__(self, other))

    def __neg__(self):
        return Number(float.__neg__(self))

    def __pos__(self):
        return Number(float.__pos__(self))

    def __abs__(self):
        return Number(float.__abs__(self))

    def __index__(self):
        """Convert to int for use as list/tuple index"""
        return int(float(self))


def wrap_number(value):
    """Convert a numeric value to a Number instance"""
    if isinstance(value, Number):
        return value
    if isinstance(value, (int, float)):
        return Number(value)
    return value
