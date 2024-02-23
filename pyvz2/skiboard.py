"""Skiboard module for keyboard input."""
# Copyright (C) 2023-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "CSISequences",
    "CtrlCodes",
    "Event",
    "KeypadActions",
    "Mouse",
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
from re import Pattern
from signal import SIGINT, raise_signal
from sys import stdin
from threading import Lock, Thread
from typing import ClassVar, Literal, Self, overload

_ADD_MODIFIABLE: Pattern[str] = re.compile(r"\x1b?[ -\x7f]")
_CSI_MODIFIABLE: Pattern[str] = re.compile(
    r"\x1bO[P-S]|\x1b\[(?:\d+(?:;\d+)?)?[A-Z~]",
)
_CTRL_C: Literal[b"\x03"] = b"\x03"
_CTRL_MODIFIABLE: Pattern[str] = re.compile(r"\x1b?[?-_a-z]")
_EOF: Literal[b""] = b""
_ESC_MODIFIABLE: Pattern[str] = re.compile(r".|\x1b[O\[].+")
_PARAM_CHARS: Literal["0123456789;"] = "0123456789;"
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

    NULL: Literal["\0"] = "\0"

    START_OF_HEADING: Literal["\x01"] = "\x01"
    START_OF_TEXT: Literal["\x02"] = "\x02"
    END_OF_TEXT: Literal["\x03"] = "\x03"
    END_OF_TRANSMISSION: Literal["\x04"] = "\x04"
    ENQUIRY: Literal["\x05"] = "\x05"
    ACKNOWLEDGE: Literal["\x06"] = "\x06"

    BELL: Literal["\a"] = "\a"
    BACKSPACE: Literal["\b"] = "\b"
    HORIZONTAL_TABULATION: Literal["\t"] = "\t"
    LINE_FEED: Literal["\n"] = "\n"
    VERTICAL_TABULATION: Literal["\v"] = "\v"
    FORM_FEED: Literal["\f"] = "\f"
    CARRIAGE_RETURN: Literal["\r"] = "\r"

    SHIFT_OUT: Literal["\x0e"] = "\x0e"
    SHIFT_IN: Literal["\x0f"] = "\x0f"
    DATA_LINK_ESCAPE: Literal["\x10"] = "\x10"
    XON: Literal["\x11"] = "\x11"
    DEVICE_CONTROL_TWO: Literal["\x12"] = "\x12"
    XOFF: Literal["\x13"] = "\x13"
    DEVICE_CONTROL_FOUR: Literal["\x14"] = "\x14"
    NEGATIVE_ACKNOWLEDGE: Literal["\x15"] = "\x15"
    SYNCHRONOUS_IDLE: Literal["\x16"] = "\x16"
    END_OF_TRANSMISSION_BLOCK: Literal["\x17"] = "\x17"
    CANCEL: Literal["\x18"] = "\x18"
    END_OF_MEDIUM: Literal["\x19"] = "\x19"
    SUBSTITUTE: Literal["\x1a"] = "\x1a"

    ESCAPE: Literal["\x1b"] = "\x1b"

    FILE_SEPARATOR: Literal["\x1c"] = "\x1c"
    GROUP_SEPARATOR: Literal["\x1d"] = "\x1d"
    RECORD_SEPARATOR: Literal["\x1e"] = "\x1e"
    UNIT_SEPARATOR: Literal["\x1f"] = "\x1f"
    DELETE: Literal["\x7f"] = "\x7f"


class KeypadActions:  # pylint: disable=too-few-public-methods
    """Class for keypad actions."""

    ENTER: Literal["\x1bOM"] = "\x1bOM"

    DELETE: Literal["\x1bOn"] = "\x1bOn"
    INSERT: Literal["\x1bOp"] = "\x1bOp"
    END: Literal["\x1bOq"] = "\x1bOq"
    DOWN: Literal["\x1bOr"] = "\x1bOr"
    PAGE_DOWN: Literal["\x1bOs"] = "\x1bOs"
    LEFT: Literal["\x1bOt"] = "\x1bOt"
    RIGHT: Literal["\x1bOv"] = "\x1bOv"
    HOME: Literal["\x1bOw"] = "\x1bOw"
    UP: Literal["\x1bOx"] = "\x1bOx"
    PAGE_UP: Literal["\x1bOy"] = "\x1bOy"


class SS3Sequences:  # pylint: disable=too-few-public-methods
    """Class for SS3 sequences."""

    SS3: Literal["\x1bO"] = "\x1bO"

    UP: Literal["\x1bOA"] = "\x1bOA"
    DOWN: Literal["\x1bOB"] = "\x1bOB"
    RIGHT: Literal["\x1bOC"] = "\x1bOC"
    LEFT: Literal["\x1bOD"] = "\x1bOD"
    END: Literal["\x1bOF"] = "\x1bOF"
    HOME: Literal["\x1bOH"] = "\x1bOH"

    KEYPAD_ENTER: Literal["\x1bOM"] = "\x1bOM"

    F1: Literal["\x1bOP"] = "\x1bOP"
    F2: Literal["\x1bOQ"] = "\x1bOQ"
    F3: Literal["\x1bOR"] = "\x1bOR"
    F4: Literal["\x1bOS"] = "\x1bOS"

    KEYPAD_EQUALS: Literal["\x1bOX"] = "\x1bOX"
    KEYPAD_MULTIPLY: Literal["\x1bOj"] = "\x1bOj"
    KEYPAD_ADD: Literal["\x1bOk"] = "\x1bOk"
    KEYPAD_COMMA: Literal["\x1bOl"] = "\x1bOl"
    KEYPAD_MINUS: Literal["\x1bOm"] = "\x1bOm"
    KEYPAD_PERIOD: Literal["\x1bOn"] = "\x1bOn"
    KEYPAD_DIVIDE: Literal["\x1bOo"] = "\x1bOo"

    KEYPAD_0: Literal["\x1bOp"] = "\x1bOp"
    KEYPAD_1: Literal["\x1bOq"] = "\x1bOq"
    KEYPAD_2: Literal["\x1bOr"] = "\x1bOr"
    KEYPAD_3: Literal["\x1bOs"] = "\x1bOs"
    KEYPAD_4: Literal["\x1bOt"] = "\x1bOt"
    KEYPAD_5: Literal["\x1bOu"] = "\x1bOu"
    KEYPAD_6: Literal["\x1bOv"] = "\x1bOv"
    KEYPAD_7: Literal["\x1bOw"] = "\x1bOw"
    KEYPAD_8: Literal["\x1bOx"] = "\x1bOx"
    KEYPAD_9: Literal["\x1bOy"] = "\x1bOy"


class CSISequences:  # pylint: disable=too-few-public-methods
    """Class for CSI sequences."""

    CSI: Literal["\x1b["] = "\x1b["

    SGR_MOUSE: Literal["\x1b[<"] = "\x1b[<"
    UP: Literal["\x1b[A"] = "\x1b[A"
    DOWN: Literal["\x1b[B"] = "\x1b[B"
    RIGHT: Literal["\x1b[C"] = "\x1b[C"
    LEFT: Literal["\x1b[D"] = "\x1b[D"
    BEGIN: Literal["\x1b[E"] = "\x1b[E"
    END: Literal["\x1b[F"] = "\x1b[F"
    NEXT: Literal["\x1b[G"] = "\x1b[G"
    HOME: Literal["\x1b[H"] = "\x1b[H"
    MOUSE: Literal["\x1b[M"] = "\x1b[M"
    MOUSE_MOVE: Literal["\x1b[T"] = "\x1b[T"
    SHIFT_TAB: Literal["\x1b[Z"] = "\x1b[Z"
    MOUSE_CLICK: Literal["\x1b[t"] = "\x1b[t"
    INSERT: Literal["\x1b[2~"] = "\x1b[2~"
    DELETE: Literal["\x1b[3~"] = "\x1b[3~"
    PAGE_UP: Literal["\x1b[5~"] = "\x1b[5~"
    PAGE_DOWN: Literal["\x1b[6~"] = "\x1b[6~"

    F5: Literal["\x1b[15~"] = "\x1b[15~"
    F6: Literal["\x1b[17~"] = "\x1b[17~"
    F7: Literal["\x1b[18~"] = "\x1b[18~"
    F8: Literal["\x1b[19~"] = "\x1b[19~"
    F9: Literal["\x1b[20~"] = "\x1b[20~"
    F10: Literal["\x1b[21~"] = "\x1b[21~"
    F11: Literal["\x1b[23~"] = "\x1b[23~"
    F12: Literal["\x1b[24~"] = "\x1b[24~"
    F13: Literal["\x1b[25~"] = "\x1b[25~"
    F14: Literal["\x1b[26~"] = "\x1b[26~"
    F15: Literal["\x1b[28~"] = "\x1b[28~"
    F16: Literal["\x1b[29~"] = "\x1b[29~"
    F17: Literal["\x1b[31~"] = "\x1b[31~"
    F18: Literal["\x1b[32~"] = "\x1b[32~"
    F19: Literal["\x1b[33~"] = "\x1b[33~"
    F20: Literal["\x1b[34~"] = "\x1b[34~"


class Mouse:  # pylint: disable=too-few-public-methods
    """Class for mouse buttons."""

    BUTTON_1: Literal[0x00] = 0x00
    BUTTON_2: Literal[0x01] = 0x01
    BUTTON_3: Literal[0x02] = 0x02
    RELEASE: Literal[0x03] = 0x03

    SHIFT: Literal[0x04] = 0x04
    ALT: Literal[0x08] = 0x08
    ALT_SHIFT: Literal[0x0c] = 0x0c
    CTRL: Literal[0x10] = 0x10
    CTRL_SHIFT: Literal[0x14] = 0x14
    CTRL_ALT: Literal[0x18] = 0x18
    CTRL_ALT_SHIFT: Literal[0x1c] = 0x1c

    BUTTON_4: Literal[0x40] = 0x40
    BUTTON_5: Literal[0x41] = 0x41
    BUTTON_6: Literal[0x42] = 0x42
    BUTTON_7: Literal[0x43] = 0x43

    BUTTON_8: Literal[0x80] = 0x80
    BUTTON_9: Literal[0x81] = 0x81
    BUTTON_10: Literal[0x82] = 0x82
    BUTTON_11: Literal[0x83] = 0x83


class _KeyReader:
    """Class to read keys from standard input."""

    byte: ClassVar[bytes | None] = None
    lock: ClassVar[Lock] = Lock()
    thread: ClassVar[Thread | None] = None

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

    __slots__: ClassVar[tuple[()]] = ()

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
