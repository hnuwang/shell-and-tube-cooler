from __future__ import annotations

import math
from typing import TypeVar

T = TypeVar("T", int, float)


class DesignError(RuntimeError):
    """Raised when no acceptable design can be found."""


def celsius_to_kelvin(temp_c: float) -> float:
    """Convert Celsius to Kelvin."""
    return temp_c + 273.15


def kelvin_to_celsius(temp_k: float) -> float:
    """Convert Kelvin to Celsius."""
    return temp_k - 273.15


def linear_interpolate(x0: float, y0: float, x1: float, y1: float, x: float) -> float:
    """Perform linear interpolation between two points."""
    if math.isclose(x1, x0):
        return y0
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def clamp(value: T, low: T, high: T) -> T:
    """Clamp a value to a closed interval."""
    return max(low, min(value, high))


def ensure_positive(value: float, name: str) -> float:
    """Ensure a numeric value is strictly positive."""
    if value <= 0.0:
        raise ValueError(f"{name} must be positive, got {value}.")
    return value
