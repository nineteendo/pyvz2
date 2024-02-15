"""Skiboard module for keyboard input."""
# Copyright (C) 2020-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "CSISequences",
    "CtrlCodes",
    "Event",
    "Mouse",
    "RawInput",
    "SS3Sequences",
    "add",
    "alt",
    "alt_meta",
    "alt_shift",
    "alt_shift_meta",
    "ctrl",
    "ctrl_alt",
    "ctrl_alt_meta",
    "ctrl_alt_shift",
    "ctrl_alt_shift_meta",
    "ctrl_esc",
    "ctrl_meta",
    "ctrl_shift",
    "ctrl_shift_meta",
    "esc",
    "esc_add",
    "get_event",
    "meta",
    "shift",
    "shift_add",
    "shift_esc",
    "shift_esc_add",
    "shift_meta",
]
__author__: str = "Nice Zombies"

import re
import sys
from abc import ABC, abstractmethod
from atexit import register
from contextlib import ContextDecorator
from re import Pattern
from signal import SIGINT, raise_signal
from sys import stdin
from threading import Lock, Thread
from typing import TYPE_CHECKING, Any, Self, overload

if TYPE_CHECKING:
    from types import TracebackType

_ADD_MODIFIABLE: Pattern[str] = re.compile(r"\x1b?[ -\x7f]")
_CSI_MODIFIABLE: Pattern[str] = re.compile(
    r"\x1bO[P-S]|\x1b\[(?:\d+(?:;\d+)?)?[A-Z~]",
)
_CTRL_C: bytes = b"\x03"
_CTRL_MODIFIABLE: Pattern[str] = re.compile(r"\x1b?[?-_a-z]")
_EOF: bytes = b""
_ESC_MODIFIABLE: Pattern[str] = re.compile(r".|\x1b[O\[].+")
_PARAM_CHARS: str = "0123456789;"
_SHIFT_MODIFIABLE: Pattern[str] = re.compile(r"\x1b?.")
_TIMEOUT: float = 0.01


# mypy: disable-error-code=no-untyped-def
def _make_modifier(modifier: int):  # noqa: ANN202
    """Make modifier function."""
    def apply_modifier(value: str) -> Event:
        """Apply modifier to value."""
        if modifier & 0x01 and _SHIFT_MODIFIABLE.fullmatch(value):
            value = value.upper()

        if modifier & 0x04 and _CTRL_MODIFIABLE.fullmatch(value):
            value = value[:-1] + chr((ord(value[-1].upper()) - 0x40) % 0x80)

        if modifier & 0x0f and _CSI_MODIFIABLE.fullmatch(value):
            # Deal with F1-F4
            value = value.replace(SS3Sequences.SS3, CSISequences.CSI)
            start, _1, end = value[:-1].partition("[")
            params: list[str] = end.split(";")
            param1: int = int(params[0]) if params[0] else 1
            param2: int = int(params[1]) if len(params) > 1 else 1
            param2 = ((param2 - 1) | modifier & 0x0f) + 1
            value = f"{start}[{param1};{param2}{value[-1]}"

        if modifier & 0x10 and _ADD_MODIFIABLE.fullmatch(value):
            value = value[:-1] + chr(ord(value[-1]) + 0x80)

        if modifier & 0x20 and _ESC_MODIFIABLE.fullmatch(value):
            value = CtrlCodes.ESCAPE + value

        return Event(value)

    return apply_modifier


shift = _make_modifier(0x01)
alt = _make_modifier(0x02)
alt_shift = _make_modifier(0x03)
ctrl = _make_modifier(0x04)
ctrl_shift = _make_modifier(0x05)
ctrl_alt = _make_modifier(0x06)
ctrl_alt_shift = _make_modifier(0x07)
meta = _make_modifier(0x08)
shift_meta = _make_modifier(0x09)
alt_meta = _make_modifier(0x0a)
alt_shift_meta = _make_modifier(0x0b)
ctrl_meta = _make_modifier(0x0c)
ctrl_shift_meta = _make_modifier(0x0d)
ctrl_alt_meta = _make_modifier(0x0e)
ctrl_alt_shift_meta = _make_modifier(0x0f)
add = _make_modifier(0x10)
shift_add = _make_modifier(0x11)
esc = _make_modifier(0x20)
shift_esc = _make_modifier(0x21)
ctrl_esc = _make_modifier(0x24)
esc_add = _make_modifier(0x30)
shift_esc_add = _make_modifier(0x31)


class CtrlCodes:  # pylint: disable=too-few-public-methods
    """Class for C0 control codes."""

    NULL: str = "\0"

    START_OF_HEADING: str = "\x01"
    START_OF_TEXT: str = "\x02"
    END_OF_TEXT: str = "\x03"
    END_OF_TRANSMISSION: str = "\x04"
    ENQUIRY: str = "\x05"
    ACKNOWLEDGE: str = "\x06"

    BELL: str = "\a"
    BACKSPACE: str = "\b"
    HORIZONTAL_TABULATION: str = "\t"
    LINE_FEED: str = "\n"
    VERTICAL_TABULATION: str = "\v"
    FORM_FEED: str = "\f"
    CARRIAGE_RETURN: str = "\r"

    SHIFT_OUT: str = "\x0e"
    SHIFT_IN: str = "\x0f"
    DATA_LINK_ESCAPE: str = "\x10"
    XON: str = "\x11"
    DEVICE_CONTROL_TWO: str = "\x12"
    XOFF: str = "\x13"
    DEVICE_CONTROL_FOUR: str = "\x14"
    NEGATIVE_ACKNOWLEDGE: str = "\x15"
    SYNCHRONOUS_IDLE: str = "\x16"
    END_OF_TRANSMISSION_BLOCK: str = "\x17"
    CANCEL: str = "\x18"
    END_OF_MEDIUM: str = "\x19"
    SUBSTITUTE: str = "\x1a"

    ESCAPE: str = "\x1b"

    FILE_SEPARATOR: str = "\x1c"
    GROUP_SEPARATOR: str = "\x1d"
    RECORD_SEPARATOR: str = "\x1e"
    UNIT_SEPARATOR: str = "\x1f"
    DELETE: str = "\x7f"


class SS3Sequences:  # pylint: disable=too-few-public-methods
    """Class for SS3 sequences."""

    SS3: str = "\x1bO"

    UP: str = "\x1bOA"
    DOWN: str = "\x1bOB"
    RIGHT: str = "\x1bOC"
    LEFT: str = "\x1bOD"
    END: str = "\x1bOF"
    HOME: str = "\x1bOH"

    KEYPAD_ENTER: str = "\x1bOM"

    F1: str = "\x1bOP"
    F2: str = "\x1bOQ"
    F3: str = "\x1bOR"
    F4: str = "\x1bOS"

    KEYPAD_EQUALS: str = "\x1bOX"
    KEYPAD_MULTIPLY: str = "\x1bOj"
    KEYPAD_ADD: str = "\x1bOk"
    KEYPAD_COMMA: str = "\x1bOl"
    KEYPAD_MINUS: str = "\x1bOm"
    KEYPAD_PERIOD: str = "\x1bOn"
    KEYPAD_DIVIDE: str = "\x1bOo"

    KEYPAD_0: str = "\x1bOp"
    KEYPAD_1: str = "\x1bOq"
    KEYPAD_2: str = "\x1bOr"
    KEYPAD_3: str = "\x1bOs"
    KEYPAD_4: str = "\x1bOt"
    KEYPAD_5: str = "\x1bOu"
    KEYPAD_6: str = "\x1bOv"
    KEYPAD_7: str = "\x1bOw"
    KEYPAD_8: str = "\x1bOx"
    KEYPAD_9: str = "\x1bOy"


class CSISequences:  # pylint: disable=too-few-public-methods
    """Class for CSI sequences."""

    CSI: str = "\x1b["

    SGR_MOUSE: str = "\x1b[<"
    UP: str = "\x1b[A"
    DOWN: str = "\x1b[B"
    RIGHT: str = "\x1b[C"
    LEFT: str = "\x1b[D"
    BEGIN: str = "\x1b[E"
    END: str = "\x1b[F"
    NEXT: str = "\x1b[G"
    HOME: str = "\x1b[H"
    MOUSE: str = "\x1b[M"
    MOUSE_MOVE: str = "\x1b[T"
    SHIFT_TAB: str = "\x1b[Z"
    MOUSE_CLICK: str = "\x1b[t"
    INSERT: str = "\x1b[2~"
    DELETE: str = "\x1b[3~"
    PAGE_UP: str = "\x1b[5~"
    PAGE_DOWN: str = "\x1b[6~"

    F5: str = "\x1b[15~"
    F6: str = "\x1b[17~"
    F7: str = "\x1b[18~"
    F8: str = "\x1b[19~"
    F9: str = "\x1b[20~"
    F10: str = "\x1b[21~"
    F11: str = "\x1b[23~"
    F12: str = "\x1b[24~"
    F13: str = "\x1b[25~"
    F14: str = "\x1b[26~"
    F15: str = "\x1b[28~"
    F16: str = "\x1b[29~"
    F17: str = "\x1b[31~"
    F18: str = "\x1b[32~"
    F19: str = "\x1b[33~"
    F20: str = "\x1b[34~"


class Mouse:  # pylint: disable=too-few-public-methods
    """Class for mouse buttons."""

    BUTTON_1: int = 0x00
    BUTTON_2: int = 0x01
    BUTTON_3: int = 0x02
    RELEASE: int = 0x03

    SHIFT: int = 0x04
    ALT: int = 0x08
    ALT_SHIFT: int = 0x0c
    CTRL: int = 0x10
    CTRL_SHIFT: int = 0x14
    CTRL_ALT: int = 0x18
    CTRL_ALT_SHIFT: int = 0x1c

    BUTTON_4: int = 0x40
    BUTTON_5: int = 0x41
    BUTTON_6: int = 0x42
    BUTTON_7: int = 0x43

    BUTTON_8: int = 0x80
    BUTTON_9: int = 0x81
    BUTTON_10: int = 0x82
    BUTTON_11: int = 0x83


class _BaseRawInput(ContextDecorator, ABC):
    """Base class for raw input."""

    count: int = 0

    def __enter__(self: Self) -> Self:
        if not _BaseRawInput.count:
            self.enable()

        _BaseRawInput.count += 1
        return self

    def __exit__(
        self: Self, _1: type[BaseException] | None, _2: BaseException | None,
        _3: TracebackType | None,
    ) -> None:
        _BaseRawInput.count = max(0, _BaseRawInput.count - 1)
        if not _BaseRawInput.count:
            self.disable()

    @classmethod
    @abstractmethod
    def disable(cls) -> None:
        """Disable raw input."""

    @classmethod
    @abstractmethod
    def enable(cls) -> None:
        """Enable raw input."""


if sys.platform == "win32":
    from ctypes import byref, c_ulong, windll
    # noinspection PyCompatibility
    from msvcrt import get_osfhandle  # pylint: disable=import-error

    _ENABLE_PROCESSED_INPUT: int = 0x0001
    _ENABLE_LINE_INPUT: int = 0x0002
    _ENABLE_ECHO_INPUT: int = 0x0004
    _ENABLE_VIRTUAL_TERMINAL_INPUT: int = 0x0200

    class RawInput(_BaseRawInput):
        """Class to enable & re-enable raw input."""

        _old: c_ulong = c_ulong()
        windll.kernel32.GetConsoleMode(
            get_osfhandle(stdin.fileno()), byref(_old),
        )

        @classmethod
        def disable(cls) -> None:
            """Disable raw input."""
            print(end="\x1b[?1000l\x1b[?1006l", flush=True)
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdin.fileno()), cls._old.value,
            )

        @classmethod
        def enable(cls) -> None:
            """Enable raw input."""
            value: int = cls._old.value
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
            print(end="\x1b[?1000h\x1b[?1006h", flush=True)
# pylint: disable=consider-using-in
elif sys.platform == "darwin" or sys.platform == "linux":  # noqa: PLR1714
    # pylint: disable=import-error
    from termios import (
        ICRNL, INLCR, ISTRIP, IXON, ONLCR, OPOST, TCSANOW, tcgetattr,
        tcsetattr,
    )
    from tty import setcbreak

    _IFLAG: int = 0
    _OFLAG: int = 1

    class RawInput(_BaseRawInput):
        """Class to enable & disable raw input."""

        if not stdin.isatty():
            err: str = "stdin doesn't refer to a terminal"
            raise RuntimeError(err)

        _old_value: list[Any] = tcgetattr(stdin)

        @classmethod
        def disable(cls) -> None:
            """Disable raw input."""
            tcsetattr(stdin, TCSANOW, cls._old_value)
            print(end="\x1b[?1000l\x1b[?1006l", flush=True)

        @classmethod
        def enable(cls) -> None:
            """Enable raw input."""
            print(end="\x1b[?1000h\x1b[?1006h", flush=True)
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
else:
    err: str = f"Unsupported platform: {sys.platform!r}"
    raise RuntimeError(err)

register(RawInput.disable)


class _KeyReader:
    """Class to read keys from standard input."""

    byte: bytes | None = None
    lock: Lock = Lock()
    thread: Thread | None = None

    @classmethod
    def read(cls, number: int, *, raw: bool = False) -> str:
        """Read from standard input."""
        result: str = ""
        for _1 in range(number):
            result += cls.read_char(raw=raw)

        return result

    # noinspection PyMissingOrEmptyDocstring
    @classmethod
    @overload
    def read_char(cls, *, raw: bool = False, timeout: None = None) -> str:
        ...

    # noinspection PyMissingOrEmptyDocstring
    @classmethod
    @overload
    def read_char(
        cls, *, raw: bool = False, timeout: float = ...,
    ) -> str | None:
        ...

    @classmethod
    def read_char(
        cls, *, raw: bool = False, timeout: float | None = None,
    ) -> str | None:
        """Read character from standard input."""
        byte: bytes | None = cls.read_byte(timeout=timeout)
        if byte is None:
            return byte

        if byte == _EOF:
            raise EOFError

        if byte == _CTRL_C:
            # HACK: Automatic handling of Ctrl+C has been disabled on Windows
            raise_signal(SIGINT)

        if raw:
            return byte.decode("latin_1")

        # Handle multi-byte characters
        byte_ord: int = ord(byte)
        if byte_ord & 0xF8 == 0xF8:  # 11111xxx
            # pylint: disable=redefined-outer-name
            # noinspection PyShadowingNames
            err: str = f"Read non-utf8 character: {byte!r}"
            raise RuntimeError(err)

        if byte_ord & 0xC0 == 0xC0:  # 11xxxxxx10xxxxxx...
            byte += cls.read_byte()

        if byte_ord & 0xE0 == 0xE0:  # 111xxxxx10xxxxxx10xxxxxx...
            byte += cls.read_byte()

        if byte_ord & 0xF0 == 0xF0:  # 1111xxxx10xxxxxx10xxxxxx10xxxxxx...
            byte += cls.read_byte()

        return byte.decode()

    # noinspection PyMissingOrEmptyDocstring
    @classmethod
    @overload
    def read_byte(cls, *, timeout: None = None) -> bytes:
        ...

    # noinspection PyMissingOrEmptyDocstring
    @classmethod
    @overload
    def read_byte(cls, *, timeout: float = ...) -> bytes | None:
        ...

    @classmethod
    def read_byte(cls, *, timeout: float | None = None) -> bytes | None:
        """Read byte from standard input."""
        while True:
            if cls.thread and cls.thread.is_alive():
                cls.thread.join(timeout)
            elif timeout is None:
                while cls.byte is None:
                    cls.read_from_stdin()
            else:
                cls.thread = Thread(target=cls.read_from_stdin, daemon=True)
                cls.thread.start()
                cls.thread.join(timeout)

            with cls.lock:
                byte, cls.byte = cls.byte, None

            return byte

    @classmethod
    def read_from_stdin(cls) -> None:
        """Read byte from standard input & store in cls.byte."""
        byte: bytes | None = stdin.buffer.read(1)  # Don't lock before read
        with cls.lock:
            cls.byte = byte


class Event(str):
    """Class to represent events."""

    __slots__: tuple[()] = ()

    @property
    def button(self: Self) -> int | None:
        """Mouse button."""
        if self.startswith((
            esc(CSISequences.SGR_MOUSE), CSISequences.SGR_MOUSE,
        )):
            return int(self[:-1].partition("<")[2].split(";")[0])

        if self.startswith((esc(CSISequences.MOUSE), CSISequences.MOUSE)):
            return ord(self[-3:-2]) - 32

        return None

    @property
    def pressed(self: Self) -> bool:
        """Is key pressed."""
        if self.startswith((
            esc(CSISequences.SGR_MOUSE), CSISequences.SGR_MOUSE,
        )):
            return self.endswith("M")

        if self.startswith((esc(CSISequences.MOUSE), CSISequences.MOUSE)):
            return ord(self[-3:-2]) - 32 & 0x03 != Mouse.RELEASE

        return True


def _get_ss3_sequence(*, timeout: float | None = None) -> str:
    """Get SS3 sequence from command line."""
    char: str | None = _KeyReader.read_char(raw=True, timeout=timeout)
    return char if char else ""


def _get_csi_sequence(*, timeout: float | None = None) -> str:
    """Get CSI sequence from command line."""
    csi_sequence: str = ""
    char: str | None = _KeyReader.read_char(raw=True, timeout=timeout)
    if char is None:
        return csi_sequence

    if CSISequences.CSI + csi_sequence + char == CSISequences.SGR_MOUSE:
        csi_sequence += char
        char = _KeyReader.read_char(raw=True)

    while char in _PARAM_CHARS:
        csi_sequence += char
        char = _KeyReader.read_char(raw=True)

    csi_sequence += char
    if CSISequences.CSI + csi_sequence == CSISequences.MOUSE_CLICK:
        csi_sequence += _KeyReader.read(2, raw=True)

    if CSISequences.CSI + csi_sequence == CSISequences.MOUSE:
        csi_sequence += _KeyReader.read(3, raw=True)

    if CSISequences.CSI + csi_sequence == CSISequences.MOUSE_MOVE:
        csi_sequence += _KeyReader.read(6, raw=True)

    return csi_sequence


# noinspection PyMissingOrEmptyDocstring
@overload
def get_event(*, timeout: None = None) -> Event:
    ...


# noinspection PyMissingOrEmptyDocstring
@overload
def get_event(*, timeout: float = ...) -> Event | None:
    ...


def get_event(*, timeout: float | None = None) -> Event | None:
    """Get event from command line."""
    key: str | None = _KeyReader.read_char(timeout=timeout)
    if key is None:
        return key

    if key != CtrlCodes.ESCAPE:
        return Event(key)

    char: str | None = _KeyReader.read_char(timeout=_TIMEOUT)
    if not char:
        return Event(key)

    key += char
    if key == SS3Sequences.SS3:
        key += _get_ss3_sequence(timeout=_TIMEOUT)
    elif key == CSISequences.CSI:
        key += _get_csi_sequence(timeout=_TIMEOUT)
    elif key == esc(CtrlCodes.ESCAPE):
        char = _KeyReader.read_char(raw=True, timeout=_TIMEOUT)
        if not char:
            return Event(key)

        key += char
        if key == CtrlCodes.ESCAPE + SS3Sequences.SS3:
            key += _get_ss3_sequence()
        elif key == CtrlCodes.ESCAPE + CSISequences.CSI:
            key += _get_csi_sequence()

    return Event(key)
