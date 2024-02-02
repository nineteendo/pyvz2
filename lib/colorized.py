"""Colorized module for formatting text."""
# Standard libraries
import sys
from atexit import register
from contextlib import ContextDecorator
from types import TracebackType
from typing import Optional

__all__: list[str] = ['ColoredOutput', 'NoCursor', 'RestoreCursor']
__all__ += [
    'alt_font', 'black', 'blink', 'blue', 'bold', 'conceal', 'cyan', 'dim',
    'double_underline', 'encircle', 'erase_in_display', 'erase_in_line',
    'frame', 'green', 'grey', 'invert', 'italic', 'lt_blue', 'lt_cyan',
    'lt_green', 'lt_grey', 'lt_magenta', 'lt_red', 'lt_yellow', 'magenta',
    'on_black', 'on_blue', 'on_cyan', 'on_green', 'on_grey', 'on_lt_blue',
    'on_lt_cyan', 'on_lt_green', 'on_lt_grey', 'on_lt_magenta', 'on_lt_red',
    'on_lt_yellow', 'on_magenta', 'on_red', 'on_white', 'on_yellow',
    'overline', 'rapid_blink', 'red', 'strikethrough', 'underline', 'white',
    'yellow'
]


def _make_formatter(start: int, end: int):
    """Make formatter function."""
    def apply_formatting(*values: object, sep: str = ' ') -> str:
        """Apply formatting to values."""
        return f'\x1b[{start}m{sep.join(map(str, values))}\x1b[{end}m'

    return apply_formatting


bold = _make_formatter(1, 22)
_dim = _make_formatter(2, 22)
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


def dim(*values: object, sep: str = ' ') -> str:
    """Apply formatting to values."""
    return grey(_dim(*values, sep))  # Fall back to grey


def erase_in_display(mode: int = 0) -> None:
    """Erase text in display."""
    print(end=f'\x1b[{mode}J')


def erase_in_line(mode: int = 0) -> None:
    """Erase text in line."""
    print(end=f'\x1b[{mode}K')


class _BaseColoredOutput(ContextDecorator):
    """Base class for colored output."""
    count: int = 0

    def __enter__(self) -> None:
        if not _BaseColoredOutput.count:
            self.enable()

        _BaseColoredOutput.count += 1

    def __exit__(
        self, _1: Optional[type[BaseException]], _2: Optional[BaseException],
        _3: Optional[TracebackType]
    ) -> None:
        _BaseColoredOutput.count = max(0, _BaseColoredOutput.count - 1)
        if not _BaseColoredOutput.count:
            self.disable()

    @classmethod
    def disable(cls) -> None:
        """Disable colored output."""

    @staticmethod
    def enable() -> None:
        """Enable colored output."""


if sys.platform == "win32":
    # Standard libraries
    from ctypes import byref, c_ulong, windll
    # noinspection PyCompatibility
    from msvcrt import get_osfhandle  # pylint: disable=import-error
    from sys import stdout

    _ENABLE_PROCESSED_OUTPUT:            int = 0x0001
    _ENABLE_WRAP_AT_EOL_OUTPUT:          int = 0x0002
    _ENABLE_VIRTUAL_TERMINAL_PROCESSING: int = 0x0004

    class ColoredOutput(_BaseColoredOutput):
        """Class to enable & re-enable colored output."""
        old: c_ulong = c_ulong()
        windll.kernel32.GetConsoleMode(
            get_osfhandle(stdout.fileno()), byref(old)
        )

        @classmethod
        def disable(cls) -> None:
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdout.fileno()), cls.old.value
            )

        @staticmethod
        def enable() -> None:
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdout.fileno()),
                _ENABLE_VIRTUAL_TERMINAL_PROCESSING |
                _ENABLE_WRAP_AT_EOL_OUTPUT | _ENABLE_PROCESSED_OUTPUT
            )
# pylint: disable=consider-using-in
elif sys.platform == 'darwin' or sys.platform == 'linux':
    class ColoredOutput(_BaseColoredOutput):
        """Class to enable & re-enable colored output."""
else:
    raise RuntimeError(f'Unsupported platform: {sys.platform!r}')


register(ColoredOutput.disable)


class NoCursor(ContextDecorator):
    """Class to hide & show cursor."""
    count: int = 0

    def __enter__(self) -> None:
        if not NoCursor.count:
            self.hide()

        NoCursor.count += 1

    def __exit__(
        self, _1: Optional[type[BaseException]], _2: Optional[BaseException],
        _3: Optional[TracebackType]
    ) -> None:
        NoCursor.count = max(0, NoCursor.count - 1)
        if not NoCursor.count:
            self.show()

    @staticmethod
    def hide() -> None:
        """Hide cursor."""
        print(end='\x1b[?25l', flush=True)

    @staticmethod
    def show() -> None:
        """Show cursor."""
        print(end='\x1b[?25h', flush=True)


register(NoCursor.show)


class RestoreCursor(ContextDecorator):
    """Class to save & restore cursor position."""

    def __enter__(self) -> None:
        self.save()

    def __exit__(
        self, _1: Optional[type[BaseException]], _2: Optional[BaseException],
        _3: Optional[TracebackType]
    ) -> None:
        self.restore()

    @staticmethod
    def restore() -> None:
        """Restore cursor position."""
        print(end='\x1b8', flush=True)

    @staticmethod
    def save() -> None:
        """Save cursor position."""
        print(end='\x1b7', flush=True)
