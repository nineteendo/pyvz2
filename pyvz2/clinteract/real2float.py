"""CLInteract helper functions for real numbers."""
# Copyright (C) 2020-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = ["Number", "Real", "format_real", "real2float"]
__author__: str = "Nice Zombies"

from cmath import inf
from math import log10
from sys import float_info
from typing import Union

Real = Union[float, int]
Number = Union[complex, Real]


def format_real(
    real: Real, *, decimal_point: str = ".", thousands_sep: str = "",
) -> str:
    """Format real using specified format."""
    string: str
    if isinstance(real, float) or -float_info.max <= real <= float_info.max:
        string = f"{real:,g}"
    else:
        # Calculate manually, too large
        exponent: int = int(round(log10(abs(real)), 6))
        mantissa: float = real / 10 ** exponent
        string = f"{mantissa:,g}e{exponent}"

    return string.translate({
        ord("."): decimal_point,
        ord(","): thousands_sep,
    })


def real2float(real: Real) -> float:
    """Convert real to float."""
    if real < -float_info.max:
        return -inf

    if real > float_info.max:
        return inf

    return float(real)
