"""AnsI/O functions for ansi colors."""
# Copyright (C) 2022-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "alt_font",
    "black",
    "black_bg",
    "blink",
    "blue",
    "blue_bg",
    "bold",
    "cyan",
    "cyan_bg",
    "dim",
    "double_underline",
    "encircle",
    "fast_blink",
    "frame",
    "green",
    "green_bg",
    "grey",
    "grey_bg",
    "hide",
    "invert",
    "italic",
    "lt_blue",
    "lt_blue_bg",
    "lt_cyan",
    "lt_cyan_bg",
    "lt_green",
    "lt_green_bg",
    "lt_grey",
    "lt_grey_bg",
    "lt_magenta",
    "lt_magenta_bg",
    "lt_red",
    "lt_red_bg",
    "lt_yellow",
    "lt_yellow_bg",
    "magenta",
    "magenta_bg",
    "overline",
    "red",
    "red_bg",
    "rgb",
    "rgb_bg",
    "strikethrough",
    "underline",
    "white",
    "white_bg",
    "yellow",
    "yellow_bg",
]
__author__: str = "Nice Zombies"


# mypy: disable-error-code=no-untyped-def
def _make_formatter(start: int, end: int):  # noqa: ANN202
    """Make formatter function."""
    def apply_formatting(text: str) -> str:
        """Apply ansi formatting to text."""
        return f"\x1b[{start}m{text}\x1b[{end}m"

    return apply_formatting


# mypy: disable-error-code=no-untyped-def
def _make_rgb_formatter(start: int, end: int):  # noqa: ANN202
    """Make RGB formatter function."""
    def apply_formatting(text: str, r: int, g: int, b: int) -> str:
        """Apply ansi formatting to value."""
        if not all(0x00 <= color <= 0xff for color in (r, g, b)):
            err: str = "r, g and b don't lay between 0 & 255"
            raise ValueError(err)

        return f"\x1b[{start};2;{r};{g};{b}m{text}\x1b[{end}m"

    return apply_formatting


bold = _make_formatter(1, 22)
dim = _make_formatter(2, 22)
italic = _make_formatter(3, 23)
underline = _make_formatter(4, 24)
blink = _make_formatter(5, 25)
fast_blink = _make_formatter(6, 25)
invert = _make_formatter(7, 27)
hide = _make_formatter(8, 28)
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
rgb = _make_rgb_formatter(38, 39)
black_bg = _make_formatter(40, 49)
red_bg = _make_formatter(41, 49)
green_bg = _make_formatter(42, 49)
yellow_bg = _make_formatter(43, 49)
blue_bg = _make_formatter(44, 49)
magenta_bg = _make_formatter(45, 49)
cyan_bg = _make_formatter(46, 49)
lt_grey_bg = _make_formatter(47, 49)
rgb_bg = _make_rgb_formatter(48, 49)
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
grey_bg = _make_formatter(100, 49)
lt_red_bg = _make_formatter(101, 49)
lt_green_bg = _make_formatter(102, 49)
lt_yellow_bg = _make_formatter(103, 49)
lt_blue_bg = _make_formatter(104, 49)
lt_magenta_bg = _make_formatter(105, 49)
lt_cyan_bg = _make_formatter(106, 49)
white_bg = _make_formatter(107, 49)
