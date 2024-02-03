"""19.io helper functions for real numbers."""
# Standard libraries
from cmath import inf
from math import log10
from sys import float_info
from typing import Union

__all__: list[str] = ['Number', 'Real']
__all__ += ['format_real', 'real2float']

Real = Union[float, int]
Number = Union[complex, Real]


def format_real(real: Real, *, sep: str = '') -> str:
    """Format real using specified format."""
    if isinstance(real, float) or -float_info.max <= real <= float_info.max:
        return f'{real:{sep}g}'

    exponent: int = int(round(log10(abs(real)), 6))
    mantissa: float = real / 10 ** exponent
    return f'{mantissa:{sep}g}e{exponent}'


def real2float(real: Real) -> float:
    """Convert real to float."""
    if real < -float_info.max:
        return -inf

    return inf if real > float_info.max else float(real)
