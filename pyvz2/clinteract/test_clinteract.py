"""CLInteract tests."""
# Copyright (C) 2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = []
__author__: str = "Nice Zombies"

from enum import Enum
from re import escape
from sys import float_info

# noinspection PyPackageRequirements
import pytest

from ._custom import Cursor, Representation, iscategory
from ._input_str import BaseTextInput
from .utils import format_real, real_to_float


def test_iscategory() -> None:
    """Test iscategory."""
    assert iscategory("\x00", "C")
    assert iscategory("A", "L")
    assert iscategory("\u0300", "M")
    assert iscategory("0", "N")
    assert iscategory("!", "P")
    assert iscategory("$", "S")
    assert iscategory(" ", "Z")


def test_cursor() -> None:
    """Test Cursor."""
    # Incorrect usage
    pytest.raises(
        ValueError, lambda: Cursor(0),
    ).match("columns is smaller than 1")
    # Correct usage
    cursor: Cursor = Cursor(9)
    assert (cursor.row, cursor.col) == (0, 0)
    cursor.wrote("")
    assert (cursor.row, cursor.col) == (0, 0)
    cursor.wrote("c" * 9)
    assert (cursor.row, cursor.col) == (0, 9)
    cursor.wrote("c")
    assert (cursor.row, cursor.col) == (1, 1)
    cursor.moved_next_line()
    assert (cursor.row, cursor.col) == (2, 0)


class MyEnum(Enum):
    """My enum."""

    FOO = 0.0


def my_function() -> None:
    """My function."""


def test_representation() -> None:
    """Test Representation."""
    # string representation
    assert not Representation()
    assert Representation(MyEnum.FOO) == "0"
    assert Representation(Exception("foo")) == "Exception: foo"
    assert Representation(lambda: "foo") == "<lambda>"
    assert Representation(my_function) == "my_function"
    assert Representation(1 + 0j) == "1+0j"
    assert Representation(0.0) == "0"
    assert Representation({}) == "{...}"
    assert Representation({"foo"}) == "{...}"
    assert Representation(10 ** 16) == "1e+16"
    assert Representation(False) == "False"  # noqa: FBT003
    assert Representation([]) == "[...]"
    assert Representation(()) == "(...)"
    # replace unprintable characters
    assert Representation("\x00") == "?"
    assert Representation("\x1f") == "?"
    assert Representation("\x7f") == "?"
    assert Representation("\x9f") == "?"


def test_base_text_input() -> None:
    """Test BaseTextInput incorrect usage."""
    pytest.raises(
        ValueError, lambda: BaseTextInput(allowed={"marks"}, unicode=False),
    ).match("there are no ascii marks")
    pytest.raises(
        ValueError, lambda: BaseTextInput(max_length=0),
    ).match("max_length is smaller than 1")
    pytest.raises(
        ValueError, lambda: BaseTextInput(min_length=-1),
    ).match("min_length doesn't lay between 0 & max_length")
    pytest.raises(
        ValueError, lambda: BaseTextInput(max_length=1, min_length=2),
    ).match("min_length doesn't lay between 0 & max_length")
    pytest.raises(
        ValueError, lambda: BaseTextInput(whitelist="\x00"),
    ).match(escape(r"whitelist contains an unprintable character: '\x00'"))
    pytest.raises(
        ValueError, lambda: BaseTextInput(max_length=1, value="c" * 2),
    ).match("value is longer than max_length")
    pytest.raises(
        ValueError, lambda: BaseTextInput(value="\x00"),
    ).match(escape(r"value contains an invalid character: '\x00'"))
    pytest.raises(
        ValueError, lambda: BaseTextInput(unicode=False, value="\xa1"),
    ).match("value contains an invalid character: '\xa1'")
    pytest.raises(
        ValueError, lambda: BaseTextInput(value="A", whitelist="B"),
    ).match("value contains an invalid character: 'A'")


def test_base_text_input_correct() -> None:
    """Test BaseTextInput correct usage."""
    BaseTextInput(max_length=1, value="c")
    BaseTextInput(allowed={"letters"}, value="A")
    BaseTextInput(allowed={"marks"}, value="\u0300")
    BaseTextInput(allowed={"numbers"}, value="0")
    BaseTextInput(allowed={"punctuations"}, value="!")
    BaseTextInput(allowed={"separators"}, value=" ")
    BaseTextInput(allowed={"symbols"}, value="$")
    BaseTextInput(value="A", whitelist="A")
    BaseTextInput(unicode=False, value="\xa1", whitelist="\xa1")
    BaseTextInput(value="A\u03000! $")
    BaseTextInput(allowed=set(), value="A\u03000! $")


def test_format_real() -> None:
    """Test format_real."""
    # built-in
    assert format_real(0.0) == "0"
    assert format_real(int(-float_info.max)) == "-1.79769e+308"
    assert format_real(int(float_info.max)) == "1.79769e+308"
    # manual
    assert format_real(-9_999999 * 10 ** 302) == "-1e+309"
    assert format_real(9_999999 * 10 ** 302) == "1e+309"
    assert format_real(-9_99999 * 10 ** 303) == "-9.99999e+308"
    assert format_real(9_99999 * 10 ** 303) == "9.99999e+308"
    # formatting
    assert format_real(1234.5) == "1234.5"
    assert format_real(1_2 * 10 ** 308) == "1.2e+309"
    assert (
        format_real(1234.5, decimal_point=",", thousands_sep=".") == "1.234,5"
    )
    assert format_real(1_2 * 10 ** 308, decimal_point=",") == "1,2e+309"


def test_real_to_float() -> None:
    """Test format_real."""
    # float
    assert real_to_float(0.0) == 0
    # int
    assert real_to_float(-(10 ** 309)) == -float_info.max
    assert real_to_float(10 ** 309) == float_info.max
