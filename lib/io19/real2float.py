"""19.io function for converting real numbers to floats."""
# Standard libraries
from cmath import inf, isnan
from math import log10
from sys import float_info
from typing import Union

__all__: list[str] = ['Number', 'Real']
__all__ += ['format_real', 'real2float']

Real = Union[float, int]
Number = Union[complex, Real]


def format_real(real: Real, thousands_separator: str) -> str:
    """Format real using specified format."""
    if (
        real in [-inf, inf] or isnan(real2float(real)) or
        -float_info.max <= real <= float_info.max
    ):
        return f'{real:{thousands_separator}g}'

    exponent: int = int(round(log10(abs(real)), 6))
    mantissa: float = real / 10 ** exponent
    return f'{mantissa:{thousands_separator}g}e{exponent}'


def real2float(real: Real) -> float:
    """
    Convert real to float.

    Converting `real < -float_info.max` & `real > float_info.max` to
    `-cmath.inf` & `cmath.inf` respectively
    """
    if real < -float_info.max:
        return -inf

    return inf if real > float_info.max else float(real)
