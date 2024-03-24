"""AnsI/O functions for ansi colors."""
# Copyright (C) 2022-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "alt_font",
    "black",
    "blink",
    "blue",
    "bold",
    "conceal",
    "cyan",
    "dim",
    "double_underline",
    "encircle",
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
    "red",
    "strikethrough",
    "underline",
    "white",
    "yellow",
]
__author__: str = "Nice Zombies"


# mypy: disable-error-code=no-untyped-def
def _make_formatter(start: int, end: int):  # noqa: ANN202
    """Make formatter function."""
    def apply_formatting(*values: object, sep: str = " ") -> str:
        """Apply ansi formatting to values."""
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
