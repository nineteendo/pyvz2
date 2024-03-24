"""CLInteract utilities for command line input."""
# Copyright (C) 2023-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = ["format_real", "real_to_float"]
__author__: str = "Nice Zombies"

from math import log10
from sys import float_info


def format_real(
    real: float,
    *,
    decimal_point: str = ".",
    thousands_sep: str = "",
) -> str:
    """Format real using specified format."""
    string: str
    if isinstance(real, float) or -float_info.max <= real <= float_info.max:
        string = f"{real:,g}"
    else:
        # Calculate manually, int too large
        exponent: int = int(log10(abs(real)))
        mantissa: float = round(real / 10 ** exponent, 5)
        if abs(mantissa) == 10:
            exponent, mantissa = exponent + 1, mantissa / 10

        string = f"{mantissa:,g}e{exponent:+}"

    return string.translate({
        ord("."): decimal_point,
        ord(","): thousands_sep,
    })


def real_to_float(real: float) -> float:
    """Convert real to float."""
    if isinstance(real, float):
        return real

    # Clamp int
    return float(max(-float_info.max, min(real, float_info.max)))
