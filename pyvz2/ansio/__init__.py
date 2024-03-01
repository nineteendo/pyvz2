"""AnsI/O module for ansi input & output."""
# Copyright (C) 2022-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "RecursiveContext",
    "application_keypad",
    "colored_output",
    "mouse_input",
    "no_cursor",
    "raw_input",
]
__author__: str = "Nice Zombies"

import sys
from atexit import register
from contextlib import ContextDecorator
from sys import stdin, stdout
from typing import TYPE_CHECKING, Any, ClassVar, Literal

if TYPE_CHECKING:
    from types import FrameType, TracebackType


class RecursiveContext(ContextDecorator):
    """Class for recursive context decorators."""

    decorators: ClassVar[list[RecursiveContext]] = []

    def __init__(self) -> None:
        """Create new recursive context instance."""
        self.count: int = 0
        register(self._disable)

    def __enter__(self) -> RecursiveContext:
        """Enter context."""
        if not self.count:
            self.enable()

        self.count += 1
        return self

    def __exit__(
        self,
        _1: type[BaseException] | None,
        _2: BaseException | None,
        _3: TracebackType | None,
    ) -> None:
        """Exit context."""
        if self.count == 1:
            self.disable()

        self.count = max(0, self.count - 1)

    def _disable(self) -> None:
        ...

    def _enable(self) -> None:
        ...

    def disable(self, *, tracked: bool = True) -> None:
        """Disable context."""
        self._disable()
        if self in self.decorators and tracked:
            self.decorators.remove(self)

    def enable(self, *, tracked: bool = True) -> None:
        """Enable context."""
        self._enable()
        if self not in self.decorators and tracked:
            self.decorators.append(self)


if sys.platform == "win32":
    from ctypes import byref, c_ulong, windll
    # noinspection PyCompatibility
    from msvcrt import get_osfhandle  # pylint: disable=import-error

    _ENABLE_PROCESSED_INPUT: Literal[0x0001] = 0x0001
    _ENABLE_LINE_INPUT: Literal[0x0002] = 0x0002
    _ENABLE_ECHO_INPUT: Literal[0x0004] = 0x0004
    _ENABLE_VIRTUAL_TERMINAL_INPUT: Literal[0x0200] = 0x0200

    _ENABLE_PROCESSED_OUTPUT: Literal[0x0001] = 0x0001
    _ENABLE_WRAP_AT_EOL_OUTPUT: Literal[0x0002] = 0x0002
    _ENABLE_VIRTUAL_TERMINAL_PROCESSING: Literal[0x0004] = 0x0004
    _DISABLE_NEWLINE_AUTO_RETURN: Literal[0x0008] = 0x0008

    class _RawInput(RecursiveContext):
        def __init__(self) -> None:
            self._old: c_ulong = c_ulong()
            windll.kernel32.GetConsoleMode(
                get_osfhandle(stdin.fileno()), byref(self._old),
            )
            super().__init__()

        def _disable(self) -> None:
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdin.fileno()), self._old.value,
            )

        def _enable(self) -> None:
            value: int = self._old.value
            # HACK: Disable processed input, Windows has one key delay
            # Disable line input and echo input
            value &= ~(
                _ENABLE_PROCESSED_INPUT | _ENABLE_LINE_INPUT
                | _ENABLE_ECHO_INPUT
            )
            value |= _ENABLE_VIRTUAL_TERMINAL_INPUT
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdin.fileno()), value,
            )

    class _ColoredOutput(RecursiveContext):
        def __init__(self) -> None:
            self._old: c_ulong = c_ulong()
            windll.kernel32.GetConsoleMode(
                get_osfhandle(stdout.fileno()), byref(self._old),
            )
            super().__init__()

        def _disable(self) -> None:
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdout.fileno()), self._old.value,
            )

        def _enable(self) -> None:
            value: int = self._old.value
            value |= (
                _ENABLE_PROCESSED_OUTPUT | _ENABLE_WRAP_AT_EOL_OUTPUT
                | _ENABLE_VIRTUAL_TERMINAL_PROCESSING
                | _DISABLE_NEWLINE_AUTO_RETURN
            )
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdout.fileno()), value,
            )
# pylint: disable=consider-using-in
elif sys.platform == "darwin" or sys.platform == "linux":
    # pylint: disable=import-error, no-name-in-module
    from signal import SIG_DFL, SIGCONT, SIGTSTP, raise_signal, signal
    from termios import (
        ICRNL, INLCR, ISTRIP, IXON, ONLCR, OPOST, TCSANOW, tcgetattr,
        tcsetattr,
    )
    from tty import setcbreak

    _IFLAG: Literal[0] = 0
    _OFLAG: Literal[1] = 1

    class _RawInput(RecursiveContext):

        def __init__(self) -> None:
            if not stdin.isatty():
                # pylint: disable=redefined-outer-name
                # noinspection PyShadowingNames
                err: str = "stdin doesn't refer to a terminal"
                raise RuntimeError(err)

            self._old_value: list[Any] = tcgetattr(stdin)
            super().__init__()

        def _disable(self) -> None:
            tcsetattr(stdin, TCSANOW, self._old_value)

        def _enable(self) -> None:  # noqa: PLR6301
            mode: list[Any] = tcgetattr(stdin)
            # Disable stripping of input to seven bits
            # Disable converting of '\r' & '\n' on input
            # Disable start/stop control on output
            mode[_IFLAG] &= ~(ISTRIP | INLCR | ICRNL | IXON)

            # Convert '\n' on output to '\r\n'
            mode[_OFLAG] |= OPOST | ONLCR
            tcsetattr(stdin, TCSANOW, mode)

            # Disable line buffering & erase/kill character-processing
            setcbreak(stdin, TCSANOW)

    _ColoredOutput = RecursiveContext

    def _resume(_1: int, _2: FrameType | None) -> None:
        """Enable all contexts on resume."""
        signal(SIGTSTP, _suspend)
        for decorator in RecursiveContext.decorators:
            decorator.enable(tracked=False)

    def _suspend(signum: int, _2: FrameType | None) -> None:
        """Disable all contexts on suspend."""
        for decorator in reversed(RecursiveContext.decorators):
            decorator.disable(tracked=False)

        signal(signum, SIG_DFL)
        raise_signal(signum)

    signal(SIGCONT, _resume)
    signal(SIGTSTP, _suspend)
else:
    err: str = f"Unsupported platform: {sys.platform!r}"
    raise RuntimeError(err)


def _make_terminal_context(start: str, end: str) -> RecursiveContext:
    class TerminalContext(RecursiveContext):
        """Class for terminal contexts."""

        def _disable(self) -> None:  # noqa: PLR6301
            print(end=end, flush=True)

        def _enable(self) -> None:  # noqa: PLR6301
            print(end=start, flush=True)

    return TerminalContext()


raw_input: RecursiveContext = _RawInput()
application_keypad: RecursiveContext = _make_terminal_context("\x1b=", "\x1b>")
mouse_input: RecursiveContext = _make_terminal_context(
    "\x1b[?1000h\x1b[?1006h", "\x1b[?1000l\x1b[?1006l",
)
colored_output: RecursiveContext = _ColoredOutput()
no_cursor: RecursiveContext = _make_terminal_context("\x1b[?25l", "\x1b[?25h")
