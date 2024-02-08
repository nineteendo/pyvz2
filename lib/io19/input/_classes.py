"""19.io type var & helper class for console input."""
__all__: list[str] = [
    # SCREAMING_SNAKE_CASE
    'VALUE',
    # PascalCase
    'ContextEvent', 'Cursor', 'Representation'
]

# Standard libraries
import re
import threading
from datetime import date, datetime, time
from enum import Enum
from re import Pattern
from types import FunctionType, TracebackType
from typing import Optional, Self, TypeVar

# Custom libraries
from ..real2float import format_real

_UNPRINTABLE: Pattern = re.compile(r'[\x00-\x1f\x7f-\x9f]')

VALUE = TypeVar('VALUE')


class ContextEvent(threading.Event):
    """Class implementing context event objects."""

    def __enter__(self) -> Self:
        self.clear()
        return self

    def __exit__(
        self, _1: Optional[type[BaseException]], _2: Optional[BaseException],
        _3: Optional[TracebackType]
    ) -> None:
        self.set()


class Cursor:
    """Class to keep track of cursor."""

    def __init__(self, columns: int) -> None:
        if columns < 1:
            raise ValueError('columns is smaller than 1')

        self.col:     int = 0
        self.row:     int = 0
        self.columns: int = columns

    def wrote(self, text: str) -> None:
        """Wrote text to stdout."""
        self.row += (self.col + len(text) - 1) // self.columns
        self.col = (self.col + len(text) - 1) % self.columns + 1

    @property
    def position(self) -> int:
        """Get cursor position."""
        return self.row * self.columns + self.col

    def moved_next_line(self) -> None:
        """Moved to next line."""
        self.row, self.col = self.row + 1, 0


class Representation(str):
    """Get a user-friendly representation from the given object."""

    def __new__(cls, obj: object = '') -> 'Self':
        for data_type, func in {
            BaseException: lambda b: cls(f'{type(b).__name__}: {b}'),
            Enum: lambda e: cls(e.value),
            FunctionType: lambda f: cls(f.__name__),
            bool: lambda b: cls(str(b)),
            complex: lambda c: cls(f'{c:g}'),
            datetime: lambda d: cls(d.strftime('%a %d %b %Y %X')),
            date: lambda d: cls(d.strftime('%a %d %b %Y')),
            dict: lambda _1: cls('{...}'),
            int: lambda i: cls(format_real(i)),
            list: lambda _1: cls('[...]'),
            time: lambda t: cls(t.strftime('%X')),
            tuple: lambda _1: cls('(...)')
        }.items():
            if isinstance(obj, data_type):
                return func(obj)

        return super().__new__(cls, _UNPRINTABLE.sub(lambda _1: '?', str(obj)))
