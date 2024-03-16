"""AnsI/O module for ansi input & output."""
# Copyright (C) 2022-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "TerminalContext",
    "application_keypad",
    "colored_output",
    "mouse_input",
    "no_cursor",
    "raw_input",
]
__author__: str = "Nice Zombies"

import sys
from atexit import register, unregister
from contextlib import ContextDecorator
from sys import stdin, stdout
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from types import FrameType, TracebackType


class TerminalContext(ContextDecorator):
    """Class for terminal context decorators."""

    decorators: ClassVar[list[TerminalContext]] = []

    def __init__(self) -> None:
        """Create new terminal context instance."""
        self.count: int = 0

    def __enter__(self) -> TerminalContext:
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
        if not stdin.isatty() or not stdout.isatty():
            # pylint: disable=redefined-outer-name
            # noinspection PyShadowingNames
            err: str = "stdin / stdout don't refer to a terminal"
            raise RuntimeError(err)

        self._disable()
        if tracked:
            unregister(self._disable)
            if self in self.decorators:
                self.decorators.remove(self)

    def enable(self, *, tracked: bool = True) -> None:
        """Enable context."""
        if not stdin.isatty() or not stdout.isatty():
            # pylint: disable=redefined-outer-name
            # noinspection PyShadowingNames
            err: str = "stdin / stdout don't refer to a terminal"
            raise RuntimeError(err)

        if tracked:
            register(self._disable)
            if self not in self.decorators:
                self.decorators.append(self)

        self._enable()


if sys.platform == "win32":
    from ctypes import byref, c_ulong, windll
    # noinspection PyCompatibility
    from msvcrt import get_osfhandle  # pylint: disable=import-error

    _ENABLE_PROCESSED_INPUT: int = 0x0001
    _ENABLE_LINE_INPUT: int = 0x0002
    _ENABLE_ECHO_INPUT: int = 0x0004
    _ENABLE_VIRTUAL_TERMINAL_INPUT: int = 0x0200

    _ENABLE_PROCESSED_OUTPUT: int = 0x0001
    _ENABLE_WRAP_AT_EOL_OUTPUT: int = 0x0002
    _ENABLE_VIRTUAL_TERMINAL_PROCESSING: int = 0x0004
    _DISABLE_NEWLINE_AUTO_RETURN: int = 0x0008

    class _RawInput(TerminalContext):
        _old_mode: int | None = None

        def _disable(self) -> None:
            if self._old_mode is not None:
                windll.kernel32.SetConsoleMode(
                    get_osfhandle(stdin.fileno()), self._old_mode,
                )
                self._old_mode = None

        def _enable(self) -> None:
            new: c_ulong = c_ulong()
            windll.kernel32.GetConsoleMode(
                get_osfhandle(stdin.fileno()), byref(new),
            )
            mode: int = new.value
            if self._old_mode is None:
                self._old_mode = mode

            # HACK: Disable processed input, Windows has one key delay
            # Disable line input and echo input
            mode &= ~(
                _ENABLE_PROCESSED_INPUT | _ENABLE_LINE_INPUT
                | _ENABLE_ECHO_INPUT
            )
            mode |= _ENABLE_VIRTUAL_TERMINAL_INPUT
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdin.fileno()), mode,
            )

    class _ColoredOutput(TerminalContext):
        _old_mode: int | None = None

        def _disable(self) -> None:
            if self._old_mode is not None:
                windll.kernel32.SetConsoleMode(
                    get_osfhandle(stdout.fileno()), self._old_mode,
                )
                self._old_mode = None

        def _enable(self) -> None:
            new: c_ulong = c_ulong()
            windll.kernel32.GetConsoleMode(
                get_osfhandle(stdout.fileno()), byref(new),
            )
            mode: int = new.value
            if self._old_mode is None:
                self._old_mode = mode

            mode |= (
                _ENABLE_PROCESSED_OUTPUT | _ENABLE_WRAP_AT_EOL_OUTPUT
                | _ENABLE_VIRTUAL_TERMINAL_PROCESSING
                | _DISABLE_NEWLINE_AUTO_RETURN
            )
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdout.fileno()), mode,
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

    _IFLAG: int = 0
    _OFLAG: int = 1

    class _RawInput(TerminalContext):
        _old_mode: list[Any] | None = None

        def _disable(self) -> None:
            if self._old_mode is not None:
                tcsetattr(stdin, TCSANOW, self._old_mode)
                self._old_mode = None

        def _enable(self) -> None:
            mode: list[Any] = tcgetattr(stdin)
            if self._old_mode is None:
                self._old_mode = tcgetattr(stdin)

            # Disable stripping of input to seven bits
            # Disable converting of '\r' & '\n' on input
            # Disable start/stop control on output
            mode[_IFLAG] &= ~(ISTRIP | INLCR | ICRNL | IXON)

            # Convert '\n' on output to '\r\n'
            mode[_OFLAG] |= OPOST | ONLCR
            tcsetattr(stdin, TCSANOW, mode)

            # Disable line buffering & erase/kill character-processing
            setcbreak(stdin, TCSANOW)

    _ColoredOutput = TerminalContext

    def _resume(_1: int, _2: FrameType | None) -> None:
        """Enable all contexts on resume."""
        signal(SIGTSTP, _suspend)
        for decorator in TerminalContext.decorators:
            decorator.enable(tracked=False)

    def _suspend(signum: int, _2: FrameType | None) -> None:
        """Disable all contexts on suspend."""
        for decorator in reversed(TerminalContext.decorators):
            decorator.disable(tracked=False)

        signal(signum, SIG_DFL)
        raise_signal(signum)

    signal(SIGCONT, _resume)
    signal(SIGTSTP, _suspend)
else:
    err: str = f"Unsupported platform: {sys.platform!r}"
    raise RuntimeError(err)


def _make_ansi_context(start: str, end: str) -> TerminalContext:
    class AnsiContext(TerminalContext):
        """Class for ansi contexts decorators."""

        def _disable(self) -> None:  # noqa: PLR6301
            print(end=end, flush=True)

        def _enable(self) -> None:  # noqa: PLR6301
            print(end=start, flush=True)

    return AnsiContext()


raw_input: TerminalContext = _RawInput()
application_keypad: TerminalContext = _make_ansi_context("\x1b=", "\x1b>")
mouse_input: TerminalContext = _make_ansi_context(
    "\x1b[?1000h\x1b[?1006h", "\x1b[?1000l\x1b[?1006l",
)
colored_output: TerminalContext = _ColoredOutput()
no_cursor: TerminalContext = _make_ansi_context("\x1b[?25l", "\x1b[?25h")
