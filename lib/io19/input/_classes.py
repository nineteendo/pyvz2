"""19.io helper classes for console input."""
# Standard libraries
import re
from datetime import date, datetime, time
from enum import Enum
from re import Pattern
from types import FunctionType
from typing import Self, TypeVar

# Custom libraries
from ..real2float import format_real

__all__: list[str] = ['VALUE']
__all__ += ['Representation']

_UNPRINTABLE: Pattern = re.compile(r'[\x00-\x1f\x7f-\x9f]')

VALUE = TypeVar('VALUE')


class Representation(str):
    """Get a user-friendly representation from the given object."""

    def __new__(cls, obj: object = '') -> Self:
        for data_type, function in {
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
                return function(obj)

        return super().__new__(cls, _UNPRINTABLE.sub(lambda _1: '?', str(obj)))
