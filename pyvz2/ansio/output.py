"""AnsI/O functions for ansi output."""
# Copyright (C) 2023-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "beep",
    "cursor_up",
    "erase_in_display",
    "erase_in_line",
    "raw_print",
    "set_cursor_position",
]
__author__: str = "Nice Zombies"

from sys import stdout


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


def set_cursor_position(row: int = 1, col: int = 1) -> None:
    """Set cursor position."""
    raw_print(f"\x1b[{row};{col}H")
