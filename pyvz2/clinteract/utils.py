"""CLInteract utilities for command line input."""
# Copyright (C) 2023-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "beep",
    "cursor_up",
    "erase_in_display",
    "erase_in_line",
    "format_real",
    "raw_print",
    "real_to_float",
    "set_cursor_position",
]
__author__: str = "Nice Zombies"

from math import log10
from sys import float_info, stdout


def beep() -> None:
    """Emit a short attention sound."""
    print(end="\a", flush=True)


def cursor_up(cells: int = 1) -> None:
    """Move cursor up."""
    if cells:
        raw_print(f"\x1b[{cells}A")


def erase_in_display(mode: int = 0) -> None:
    """Erase text in display."""
    raw_print(f"\x1b[{mode}J")


def erase_in_line(mode: int = 0) -> None:
    """Erase text in line."""
    raw_print(f"\x1b[{mode}K")


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


def raw_print(
    *values: object,
    sep: str = " ",
    end: str = "",
    flush: bool = False,
) -> None:
    """Print to stdout without automatic flusing."""
    stdout.buffer.write((sep.join(map(str, values)) + end).encode())
    if flush:
        stdout.buffer.flush()


def real_to_float(real: float) -> float:
    """Convert real to float."""
    if isinstance(real, float):
        return real

    # Clamp int
    return float(max(-float_info.max, min(real, float_info.max)))


def set_cursor_position(row: int = 1, col: int = 1) -> None:
    """Set cursor position."""
    raw_print(f"\x1b[{row};{col}H")
