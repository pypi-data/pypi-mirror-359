from typing import TypeVar

ScalarT = TypeVar("ScalarT", int, float, str, bool)
"""TypeVar for scalar-like types: int, float, str, bool"""

NumericT = TypeVar("NumericT", int, float)
"""TypeVar for numeric types: int and float"""
