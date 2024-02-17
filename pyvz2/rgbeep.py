"""RGBeep module for formatting text."""
# Copyright (C) 2020-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "alt_font",
    "beep",
    "black",
    "blink",
    "blue",
    "bold",
    "conceal",
    "cursor_up",
    "cyan",
    "dim",
    "double_underline",
    "encircle",
    "erase_in_display",
    "erase_in_line",
    "frame",
    "green",
    "grey",
    "invert",
    "italic",
    "lt_blue",
    "lt_cyan",
    "lt_green",
    "lt_grey",
    "lt_magenta",
    "lt_red",
    "lt_yellow",
    "magenta",
    "on_black",
    "on_blue",
    "on_cyan",
    "on_green",
    "on_grey",
    "on_lt_blue",
    "on_lt_cyan",
    "on_lt_green",
    "on_lt_grey",
    "on_lt_magenta",
    "on_lt_red",
    "on_lt_yellow",
    "on_magenta",
    "on_red",
    "on_white",
    "on_yellow",
    "overline",
    "rapid_blink",
    "raw_print",
    "red",
    "set_cursor_position",
    "strikethrough",
    "underline",
    "white",
    "yellow",
]
__author__: str = "Nice Zombies"

from sys import stdout


# mypy: disable-error-code=no-untyped-def
def _make_formatter(start: int, end: int):  # noqa: ANN202
    """Make formatter function."""
    def apply_formatting(*values: object, sep: str = " ") -> str:
        """Apply formatting to values."""
        return f"\x1b[{start}m{sep.join(map(str, values))}\x1b[{end}m"

    return apply_formatting


bold = _make_formatter(1, 22)
dim = _make_formatter(2, 22)
italic = _make_formatter(3, 23)
underline = _make_formatter(4, 24)
blink = _make_formatter(5, 25)
rapid_blink = _make_formatter(6, 25)
invert = _make_formatter(7, 27)
conceal = _make_formatter(8, 28)
strikethrough = _make_formatter(9, 29)
alt_font = _make_formatter(11, 10)
double_underline = _make_formatter(21, 24)
black = _make_formatter(30, 39)
red = _make_formatter(31, 39)
green = _make_formatter(32, 39)
yellow = _make_formatter(33, 39)
blue = _make_formatter(34, 39)
magenta = _make_formatter(35, 39)
cyan = _make_formatter(36, 39)
lt_grey = _make_formatter(37, 39)
on_black = _make_formatter(40, 49)
on_red = _make_formatter(41, 49)
on_green = _make_formatter(42, 49)
on_yellow = _make_formatter(43, 49)
on_blue = _make_formatter(44, 49)
on_magenta = _make_formatter(45, 49)
on_cyan = _make_formatter(46, 49)
on_lt_grey = _make_formatter(47, 49)
frame = _make_formatter(51, 54)
encircle = _make_formatter(52, 54)
overline = _make_formatter(53, 55)
grey = _make_formatter(90, 39)
lt_red = _make_formatter(91, 39)
lt_green = _make_formatter(92, 39)
lt_yellow = _make_formatter(93, 39)
lt_blue = _make_formatter(94, 39)
lt_magenta = _make_formatter(95, 39)
lt_cyan = _make_formatter(96, 39)
white = _make_formatter(97, 39)
on_grey = _make_formatter(100, 49)
on_lt_red = _make_formatter(101, 49)
on_lt_green = _make_formatter(102, 49)
on_lt_yellow = _make_formatter(103, 49)
on_lt_blue = _make_formatter(104, 49)
on_lt_magenta = _make_formatter(105, 49)
on_lt_cyan = _make_formatter(106, 49)
on_white = _make_formatter(107, 49)


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
    *values: object, sep: str = " ", end: str = "", flush: bool = False,
) -> None:
    """Print to stdout without automatic flusing."""
    stdout.buffer.write((sep.join(map(str, values)) + end).encode())
    if flush:
        stdout.buffer.flush()


def set_cursor_position(row: int = 1, col: int = 1) -> None:
    """Set cursor position."""
    raw_print(f"\x1b[{row};{col}H")
