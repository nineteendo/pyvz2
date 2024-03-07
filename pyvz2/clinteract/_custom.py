"""CLInteract typevar, classes & functions for custom command line input."""
# Copyright (C) 2023-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "VALUE",
    "ContextEvent",
    "Cursor",
    "Representation",
    "get_contexts",
    "get_shortcuts",
]
__author__: str = "Nice Zombies"

import re
from datetime import date, datetime, time
from enum import Enum
from re import Pattern
from threading import Event
from types import FunctionType
from typing import TYPE_CHECKING, ClassVar, TypeVar

from ansio import TerminalContext, application_keypad, mouse_input

from .utils import format_real

if TYPE_CHECKING:
    from types import TracebackType


_UNPRINTABLE: Pattern[str] = re.compile(r"[\x00-\x1f\x7f-\x9f]")

VALUE = TypeVar("VALUE")


def get_contexts() -> list[TerminalContext]:
    """Get (a copy of) the default contexts."""
    return [application_keypad, mouse_input]


def get_shortcuts() -> dict[str, list[str]]:
    """Get (a copy of) the default shortcuts."""
    return {
        "Cancel": ["escape"],
        "Clear screen": ["ctrl+l"],
        "Delete char after cursor": ["ctrl+d", "delete"],
        "Delete char before cursor": ["backspace", "ctrl+h"],
        "Delete everything after cursor": ["ctrl+end", "ctrl+k"],
        "Delete everything before cursor": ["ctrl+home", "ctrl+u"],
        "Delete whole line": ["escape"],
        "Move cursor back": ["ctrl+b", "left"],
        "Move cursor forward": ["ctrl+f", "right"],
        "Move cursor to end": ["ctrl+e", "end"],
        "Move cursor to start": ["ctrl+a", "home"],
        "Scroll cursor back": [],
        "Scroll cursor forward": [],
        "Submit input": ["enter", "middle_click"],
    }


class ContextEvent(Event):
    """Class implementing context event objects."""

    def __enter__(self) -> ContextEvent:
        """Enter context."""
        self.clear()
        return self

    def __exit__(
        self,
        _1: type[BaseException] | None,
        _2: BaseException | None,
        _3: TracebackType | None,
    ) -> None:
        """Exit context."""
        self.set()


class Cursor:
    """Class to keep track of cursor."""

    def __init__(self, columns: int) -> None:
        if columns < 1:
            err: str = "columns is smaller than 1"
            raise ValueError(err)

        self.col: int = 0
        self.row: int = 0
        self.columns: int = columns

    def wrote(self, text: str) -> None:
        """Notify wrote text to stdout."""
        self.row += (self.col + len(text) - 1) // self.columns
        self.col = (self.col + len(text) - 1) % self.columns + 1

    def moved_next_line(self) -> None:
        """Notify moved to next line."""
        self.row, self.col = self.row + 1, 0


class Representation(str):
    """Get a user-friendly representation from the given object."""

    __slots__: ClassVar[tuple[()]] = ()

    # noinspection PyTypeHints
    def __new__(cls, obj: object = "", /) -> Representation:  # noqa: C901
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
