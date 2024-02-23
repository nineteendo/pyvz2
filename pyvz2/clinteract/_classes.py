"""CLInteract type var & helper classes for command line input."""
# Copyright (C) 2023-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = ["VALUE", "Cursor", "Representation"]
__author__: str = "Nice Zombies"

import re
from datetime import date, datetime, time
from enum import Enum
from re import Pattern
from types import FunctionType
from typing import ClassVar, Self, TypeVar

from .real2float import format_real

_UNPRINTABLE: Pattern[str] = re.compile(r"[\x00-\x1f\x7f-\x9f]")

VALUE = TypeVar("VALUE")


class Cursor:
    """Class to keep track of cursor."""

    def __init__(self: Self, columns: int) -> None:
        if columns < 1:
            err: str = "columns is smaller than 1"
            raise ValueError(err)

        self.col: int = 0
        self.row: int = 0
        self.columns: int = columns

    def wrote(self: Self, text: str) -> None:
        """Wrote text to stdout."""
        self.row += (self.col + len(text) - 1) // self.columns
        self.col = (self.col + len(text) - 1) % self.columns + 1

    def moved_next_line(self: Self) -> None:
        """Notify cursor has moved to next line."""
        self.row, self.col = self.row + 1, 0


class Representation(str):
    """Get a user-friendly representation from the given object."""

    __slots__: ClassVar[tuple[()]] = ()

    # noinspection PyTypeHints
    def __new__(cls: type[Self], obj: object = "") -> Self:  # noqa: C901
        if isinstance(obj, BaseException):
            obj = f"{type(obj).__name__}: {obj}"
        elif isinstance(obj, Enum):
            obj = obj.value
        elif isinstance(obj, FunctionType):
            obj = obj.__name__
        elif isinstance(obj, complex):
            obj = f"{obj:g}"
        elif isinstance(obj, datetime):
            obj = obj.strftime("%a %d %b %Y %X")
        elif isinstance(obj, date):
            obj = obj.strftime("%a %d %b %Y")
        elif isinstance(obj, dict):
            obj = "{...}"
        elif isinstance(obj, int) and not isinstance(obj, bool):
            obj = format_real(obj)
        elif isinstance(obj, list):
            obj = "[...]"
        elif isinstance(obj, time):
            obj = obj.strftime("%X")
        elif isinstance(obj, tuple):
            obj = "(...)"

        return super().__new__(cls, _UNPRINTABLE.sub(lambda _1: "?", str(obj)))
