"""Contextile module for additional contexts."""
# Copyright (C) 2020-2024 Nice Zombies
from __future__ import annotations

from atexit import register
from threading import Event

__all__: list[str] = [
    "ContextEvent",
    "RecursiveContextDecorator",
    "application_keypad",
    "colored_output",
    "mouse_input",
    "no_cursor",
    "raw_input",
]
__author__: str = "Nice Zombies"

import sys
from contextlib import ContextDecorator
from sys import stdin, stdout
from typing import TYPE_CHECKING, Any, Literal, Self

if TYPE_CHECKING:
    from types import FrameType, TracebackType


class ContextEvent(Event):
    """Class implementing context event objects."""

    def __enter__(self: Self) -> Self:
        """Enter context."""
        self.clear()
        return self

    def __exit__(
        self: Self, _1: type[BaseException] | None, _2: BaseException | None,
        _3: TracebackType | None,
    ) -> None:
        """Exit context."""
        self.set()


class RecursiveContextDecorator(ContextDecorator):
    """Class for recursive context decorators."""

    def __init__(self: Self) -> None:
        """Create new recursive context decorator instance."""
        self.count: int = 0
        register(self.disable)

    def __enter__(self: Self) -> Self:
        """Enter context."""
        if not self.count:
            self.enable()

        self.count += 1
        return self

    def __exit__(
        self: Self, _1: type[BaseException] | None, _2: BaseException | None,
        _3: TracebackType | None,
    ) -> None:
        """Exit context."""
        self.count = max(0, self.count - 1)
        if not self.count:
            self.disable()

    def disable(self: Self) -> None:
        """Disable context."""

    def enable(self: Self) -> None:
        """Enable context."""


class _ApplicationKeypad(RecursiveContextDecorator):
    def disable(self) -> None:  # noqa: PLR6301
        print(end="\x1b>", flush=True)

    def enable(self) -> None:  # noqa: PLR6301
        print(end="\x1b=", flush=True)


class _MouseInput(RecursiveContextDecorator):
    def disable(self) -> None:  # noqa: PLR6301
        print(end="\x1b[?1000l\x1b[?1006l", flush=True)

    def enable(self) -> None:  # noqa: PLR6301
        print(end="\x1b[?1000h\x1b[?1006h", flush=True)


class _NoCursor(RecursiveContextDecorator):
    def disable(self: Self) -> None:  # noqa: PLR6301
        print(end="\x1b[?25h", flush=True)

    def enable(self: Self) -> None:  # noqa: PLR6301
        print(end="\x1b[?25l", flush=True)


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

    class _RawInput(RecursiveContextDecorator):
        def __init__(self: Self) -> None:
            self._old: c_ulong = c_ulong()
            windll.kernel32.GetConsoleMode(
                get_osfhandle(stdin.fileno()), byref(self._old),
            )
            super().__init__()

        def disable(self) -> None:
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdin.fileno()), self._old.value,
            )

        def enable(self) -> None:
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

    class _ColoredOutput(RecursiveContextDecorator):
        def __init__(self: Self) -> None:
            self._old: c_ulong = c_ulong()
            windll.kernel32.GetConsoleMode(
                get_osfhandle(stdout.fileno()), byref(self._old),
            )
            super().__init__()

        def disable(self: Self) -> None:
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdout.fileno()), self._old.value,
            )

        def enable(self: Self) -> None:
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
elif sys.platform == "darwin" or sys.platform == "linux":  # noqa: PLR1714
    # pylint: disable=import-error
    from termios import (
        ICRNL, INLCR, ISTRIP, IXON, ONLCR, OPOST, TCSANOW, tcgetattr,
        tcsetattr,
    )
    from tty import setcbreak

    _IFLAG: Literal[0] = 0
    _OFLAG: Literal[1] = 1

    class _RawInput(RecursiveContextDecorator):

        def __init__(self: Self) -> None:
            if not stdin.isatty():
                # pylint: disable=redefined-outer-name
                # noinspection PyShadowingNames
                err: str = "stdin doesn't refer to a terminal"
                raise RuntimeError(err)

            self._old_value: list[Any] = tcgetattr(stdin)
            super().__init__()

        def disable(self) -> None:
            tcsetattr(stdin, TCSANOW, self._old_value)

        def enable(self) -> None:  # noqa: PLR6301
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

    _ColoredOutput = RecursiveContextDecorator
else:
    err: str = f"Unsupported platform: {sys.platform!r}"
    raise RuntimeError(err)

raw_input: RecursiveContextDecorator = _RawInput()
application_keypad: RecursiveContextDecorator = _ApplicationKeypad()
mouse_input: RecursiveContextDecorator = _MouseInput()
colored_output: RecursiveContextDecorator = _ColoredOutput()
no_cursor: RecursiveContextDecorator = _NoCursor()


# pylint: disable=consider-using-in
if sys.platform == "darwin" or sys.platform == "linux":  # noqa: PLR1714
    # pylint: disable=no-name-in-module
    from signal import SIG_DFL, SIGCONT, SIGTSTP, raise_signal, signal

    def resume(_1: int, _2: FrameType | None) -> None:
        """Enable all contexts on resume."""
        signal(SIGTSTP, suspend)
        if raw_input.count:
            raw_input.enable()

        if application_keypad.count:
            application_keypad.enable()

        if mouse_input.count:
            mouse_input.enable()

        if no_cursor.count:
            no_cursor.enable()

    def suspend(_1: int, _2: FrameType | None) -> None:
        """Disable all contexts on suspend."""
        no_cursor.disable()
        mouse_input.disable()
        application_keypad.disable()
        raw_input.disable()
        signal(SIGTSTP, SIG_DFL)
        raise_signal(SIGTSTP)

    signal(SIGCONT, resume)
    signal(SIGTSTP, suspend)
