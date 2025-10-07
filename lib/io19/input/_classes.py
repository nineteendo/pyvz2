"""19.io helper classes for command line input."""
# Linting arguments
# pylint: disable=useless-suppression
# ...
# pylint: disable=too-few-public-methods

# Standard libraries
from datetime import date, datetime, time
from enum import Enum
from re import sub
from types import FunctionType
from typing import Generic, NoReturn, TypeVar

# Custom libraries
from ..real2float import format_real
from .keyboard import UNPRINTABLE

__all__: list[str] = ['ENUM', 'KEY', 'KEYINFO', 'RESULT', 'VALUE', 'VALUEINFO']
__all__ += ['CursorPosition', 'Exit', 'Info', 'Representation', 'Unique']

ENUM = TypeVar('ENUM', bound=Enum)
KEY = TypeVar('KEY')
KEYINFO = TypeVar('KEYINFO', 'Info', NoReturn)
RESULT = TypeVar('RESULT')
VALUE = TypeVar('VALUE')
VALUEINFO = TypeVar('VALUEINFO', 'Info', NoReturn)


class CursorPosition:
    """Keep track of cursor position by adding & subtracting characters."""

    def __init__(self, width: int, *, col: int = 1, row: int = 1) -> None:
        """Make new CursorPosition instance."""
        if not 1 <= col <= width + 1:
            raise ValueError('col must lay between 1 & width + 1')

        if row < 1:
            raise ValueError('row must be greater than 0')

        if width <= 0:
            raise ValueError('width must be greater than 0')

        self._col: int = col - 1
        self._row: int = row - 1
        self._width: int = width

    def __add__(self, num: int) -> 'CursorPosition':
        """Add num characters."""
        if num < 0:
            raise ValueError('num must be greater than 0')

        return CursorPosition(
            self._width, col=(self._col + num - 1) % self._width + 2,
            row=self._row + (self._col + num - 1) // self._width + 1
        )

    def __repr__(self) -> str:
        """Get representation of CursorPosition."""
        return (
            f'CursorPosition(col={self.col}, row={self.row}, width=' +
            f'{self.width})'
        )

    @property
    def chars(self) -> int:
        """Number of characters."""
        return self._row * self._width + self._col

    @property
    def col(self) -> int:
        """Current column."""
        return self._col + 1

    def move_back(self, num: int) -> None:
        """Move num characters back."""
        if num < 0:
            raise ValueError('num must be greater than 0')

        col: int = (self._col - num) % self._width
        row: int = self._row + (self._col - num) // self._width
        self._row, self._col = (0, 0) if row < 0 else (row, col)

    def next_row(self) -> None:
        """Go to next row."""
        self._row, self._col = self._row + 1, 0

    @property
    def row(self) -> int:
        """Current row."""
        return self._row + 1

    @property
    def width(self) -> int:
        """Current width."""
        return self._width

    @width.setter
    def width(self, width: int) -> None:
        """Set current width."""
        if self.chars:
            raise RuntimeError('chars must be 0')

        self._width = width


class Representation(str):
    """Get a user-friendly representation from the given object."""

    def __new__(cls, obj: object) -> 'Representation':
        """Get human-readable representation of `obj`."""
        for data_type, function in {
            BaseException: lambda b: cls(f'{type(b).__name__}: {b}'),
            Enum: lambda e: cls(e.value),
            Exit: lambda e: cls(e.value),
            FunctionType: lambda f: cls(f.__name__),
            Unique: lambda u: cls(u.value),
            bool: lambda b: cls(str(b)),
            complex: lambda c: cls(f'{c:g}'),
            datetime: lambda d: cls(d.strftime('%a %d %b %Y %X')),
            date: lambda d: cls(d.strftime('%a %d %b %Y')),
            dict: lambda _1: cls('{...}'),
            int: lambda i: cls(format_real(i, '')),
            list: lambda _1: cls('[...]'),
            time: lambda t: cls(t.strftime('%X')),
            tuple: lambda _1: cls('(...)')
        }.items():
            if isinstance(obj, data_type):
                return function(obj)

        return super().__new__(cls, sub(UNPRINTABLE, lambda _1: '?', str(obj)))


class Unique(Generic[VALUE]):
    """Unique option."""

    def __init__(self, value: VALUE) -> None:
        """Create new Unique option."""
        self.value: VALUE = value

    def __repr__(self) -> str:
        """Get representation of Unique option."""
        return f'Unique(value={self.value!r})'

    def __str__(self) -> str:
        """Get human-readable representation of `self.value`."""
        return str(self.value)


class Info(Unique[VALUE]):
    """
    Unselectable (& unique) option.

    Can be used to display additional information.
    """

    def __repr__(self) -> str:
        """Get representation of Info option."""
        return f'Info(value={self.value!r})'


class Exit(Generic[VALUE]):
    """Selectable option with yellow back cursor."""

    def __init__(self, value: VALUE) -> None:
        """Create new Exit option."""
        self.value: VALUE = value

    def __eq__(self, __value: object) -> bool:
        """Compare two Exit options."""
        return isinstance(__value, Exit) and __value.value == self.value

    def __hash__(self) -> int:
        """Get hash of `self.value`."""
        return hash(self.value)

    def __repr__(self) -> str:
        """Get representation of Exit option."""
        return f'Exit(value={self.value!r})'

    def __str__(self) -> str:
        """Get human-readable representation of `self.value`."""
        return str(self.value)
