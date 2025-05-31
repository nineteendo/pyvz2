"""Test pyvz2 utility functions."""
from __future__ import annotations
import sys

__all__: list[str] = []

from utils import parse_path

import pytest


@pytest.mark.skipif(sys.platform == "win32", reason="Only for Linux")
@pytest.mark.parametrize(("s", "expected"), [
    # One character
    ("a", "a"),

    # Multiple characters
    ("foo", "foo"),

    # Internal spaces
    ("foo bar", "foo bar"),
    ("foo  bar", "foo  bar"),

    # Quoted text
    (r'" "', " "),
    (r"' '", " "),

    # Escapes
    (r"\\", "\\"),
    (r"\ ", " "),
    (r'\"', '"'),
    (r"\'", "'"),

    # Escapes in quoted text
    (r'"\""', '"'),
    (r"'\''", "'"),

    # Escaped characters
    (r"\a", r"\a"),

    # Leading and trailing spaces
    (" foo", "foo"),
    ("foo ", "foo"),

    # Trailing backslash
    ("\\", "\\"),
])
def test_parse_path_linux(s: str, expected: str) -> None:
    """Test parse path on Linux."""
    assert parse_path(s) == expected


@pytest.mark.skipif(sys.platform != "win32", reason="Only for Windows")
@pytest.mark.parametrize(("s", "expected"), [
    # One character
    ("a", "a"),

    # Multiple characters
    ("foo", "foo"),

    # Internal spaces
    ("foo bar", "foo bar"),
    ("foo  bar", "foo  bar"),

    # Quoted text
    (r'" "', " "),
    (r"' '", "' '"),

    # Escapes
    (r"\\", r"\\"),
    (r"\ ", "\\"),
    (r'\"', '\\'),
    (r"\'", r"\'"),

    # Escapes in quoted text
    (r'"\""', '\\'),
    (r"'\''", r"'\''"),

    # Escaped characters
    (r"\a", r"\a"),

    # Leading and trailing spaces
    (" foo", "foo"),
    ("foo ", "foo"),

    # Trailing backslash
    ("\\", "\\"),
])
def test_parse_path_windows(s: str, expected: str) -> None:
    """Test parse path on Windows."""
    assert parse_path(s) == expected
