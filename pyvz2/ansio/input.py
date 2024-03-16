"""AnsI/O functions for ansi input."""
# Copyright (C) 2023-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "INPUT_EVENTS",
    "MOUSE_BUTTONS",
    "EndOfStdinError",
    "InputEvent",
    "get_input_event",
    "wait_for_stdin",
]
__author__: str = "Nice Zombies"

import re
import sys
from re import Pattern
from signal import SIGINT, raise_signal
from sys import stdin
from typing import BinaryIO, ClassVar, overload

_ALT_SEQUENCE: Pattern[str] = re.compile(r"\x1b.|\x1b\x1b[O\[].+")
_CTRL_SEQUENCE: Pattern[str] = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1a\x1c-\x1f]",
)
_MODIFIER_SEQUENCE: Pattern[str] = re.compile(r"\x1b\[\d+;\d+[A-Z~]")
_MOUSE_SEQUENCE: Pattern[str] = re.compile(r"\x1b?\x1b\[M...")
_PARAM_CHARS: str = "0123456789;"
_SGR_MOUSE_SEQUENCE: Pattern[str] = re.compile(r"\x1b?\x1b\[<\d+;\d+;\d+[Mm]")
_SHIFT_SEQUENCE: Pattern[str] = re.compile(r"\x1b.")
_TIMEOUT: float = 0.01

INPUT_EVENTS: dict[str, str] = {
    # C0 controls
    "\t": "tab",
    "\n": "enter",
    "\r": "enter",
    "\x1b": "escape",
    "\x20": "space",
    "\x7f": "backspace",

    # SS3 Sequences
    "\x1bOA": "up",
    "\x1bOB": "down",
    "\x1bOC": "right",
    "\x1bOD": "left",
    "\x1bOE": "begin",
    "\x1bOF": "end",
    "\x1bOH": "home",
    "\x1bOM": "enter",
    "\x1bOP": "f1",
    "\x1bOQ": "f2",
    "\x1bOR": "f3",
    "\x1bOS": "f4",
    "\x1bOX": "numpad_equals",
    "\x1bOj": "numpad_multiply",
    "\x1bOk": "numpad_add",
    "\x1bOl": "numpad_decimal",
    "\x1bOm": "numpad_subtract",
    "\x1bOn": "delete",
    "\x1bOo": "numpad_divide",
    "\x1bOp": "insert",
    "\x1bOq": "end",
    "\x1bOr": "down",
    "\x1bOs": "pagedown",
    "\x1bOt": "left",
    "\x1bOu": "begin",
    "\x1bOv": "right",
    "\x1bOw": "home",
    "\x1bOx": "up",
    "\x1bOy": "pageup",

    # CSI Sequences
    "\x1b[A": "up",
    "\x1b[B": "down",
    "\x1b[C": "right",
    "\x1b[D": "left",
    "\x1b[E": "begin",
    "\x1b[F": "end",
    "\x1b[H": "home",
    "\x1b[I": "focus",
    "\x1b[O": "unfocus",
    "\x1b[P": "f1",  # For modifier+f1
    "\x1b[Q": "f2",  # For modifier+f2
    "\x1b[R": "f3",  # For modifier+f3
    "\x1b[S": "f4",  # For modifier+f4
    "\x1b[1~": "home",
    "\x1b[2~": "insert",
    "\x1b[3~": "delete",
    "\x1b[4~": "end",
    "\x1b[5~": "pageup",
    "\x1b[6~": "pagedown",
    "\x1b[15~": "f5",
    "\x1b[17~": "f6",
    "\x1b[18~": "f7",
    "\x1b[19~": "f8",
    "\x1b[20~": "f9",
    "\x1b[21~": "f10",
    "\x1b[23~": "f11",
    "\x1b[24~": "f12",
    "\x1b[25~": "f13",
    "\x1b[26~": "f14",
    "\x1b[28~": "f15",
    "\x1b[29~": "f16",
    "\x1b[31~": "f17",
    "\x1b[32~": "f18",
    "\x1b[33~": "f19",
    "\x1b[34~": "f20",
}
MOUSE_BUTTONS: dict[int, str] = {
    0x00: "primary_click",
    0x01: "middle_click",
    0x02: "secondary_click",
    0x03: "no_button",
    0x40: "scrollup",
    0x41: "scrolldown",
    0x42: "button6",
    0x43: "button7",
    0x80: "button8",
    0x81: "button9",
    0x82: "button10",
    0x83: "button11",
}

if sys.platform == "win32":
    from msvcrt import kbhit  # pylint: disable=import-error
    from time import sleep, time

    _TIMEOUT_STEP: float = 0.001

    def wait_for_stdin(timeout: float | None = None) -> bool:
        """Wait until a keypress is ready to be read."""
        start_time: float = time()
        while not kbhit() and (
            timeout is None
            or time() < start_time + timeout
        ):
            sleep(_TIMEOUT_STEP)

        return kbhit()
# pylint: disable=consider-using-in
elif sys.platform == "darwin" or sys.platform == "linux":
    from select import select

    def wait_for_stdin(timeout: float | None = None) -> bool:
        """Wait until a keypress is ready to be read."""
        return bool(select([stdin.buffer], [], [], timeout)[0])
else:
    err: str = f"Unsupported platform: {sys.platform!r}"
    raise RuntimeError(err)


class EndOfStdinError(EOFError):
    """Read beyond end of stdin."""


# noinspection PyMissingOrEmptyDocstring
@overload
def _read_stdin_char(*, timeout: None = None, unicode: bool = False) -> str:
    ...


# noinspection PyMissingOrEmptyDocstring
@overload
def _read_stdin_char(
    *,
    timeout: float = ...,
    unicode: bool = False,
) -> str | None:
    ...


def _read_stdin_char(
    *,
    timeout: float | None = None,
    unicode: bool = False,
) -> str | None:
    """Read character from standard input."""
    if not wait_for_stdin(timeout):
        return None

    raw_stdin: BinaryIO = getattr(stdin.buffer, "raw", stdin.buffer)
    byte: bytes = raw_stdin.read(1)
    if not byte:
        raise EndOfStdinError

    if byte == b"\x03":
        # HACK: Automatic handling of Ctrl+C has been disabled on Windows
        raise_signal(SIGINT)

    if not unicode:
        return byte.decode("latin_1")

    # Handle multi-byte characters
    byte_ord: int = ord(byte)
    if byte_ord & 0xF8 == 0xF8:  # 11111xxx
        # pylint: disable=redefined-outer-name
        # noinspection PyShadowingNames
        err: str = f"Read non-utf8 character: {byte!r}"
        raise RuntimeError(err)

    if byte_ord & 0xC0 == 0xC0:  # 11xxxxxx10xxxxxx...
        byte += raw_stdin.read(1)

    if byte_ord & 0xE0 == 0xE0:  # 111xxxxx10xxxxxx10xxxxxx...
        byte += raw_stdin.read(1)

    if byte_ord & 0xF0 == 0xF0:  # 1111xxxx10xxxxxx10xxxxxx10xxxxxx...
        byte += raw_stdin.read(1)

    return byte.decode()


def _read_stdin(number: int, *, unicode: bool = False) -> str:
    """Read from standard input."""
    result: str = ""
    for _1 in range(number):
        result += _read_stdin_char(unicode=unicode)

    return result


class InputEvent(str):
    """Class to represent input events."""

    __slots__: ClassVar[tuple[str]] = ("shortcut",)

    def __init__(self, event: str, /) -> None:
        """Create new input event instance."""
        shift: bool = False
        if _SHIFT_SEQUENCE.fullmatch(event) and event.isupper():
            # Handle alt+shift+letter
            shift, event = True, event.lower()

        alt: bool = False
        if _ALT_SEQUENCE.fullmatch(event):
            alt, event = True, event[1:]

        ctrl: bool = False
        if _CTRL_SEQUENCE.fullmatch(event):  # Handle ctrl+letter
            ctrl, event = True, chr(0x40 + ord(event)).lower()

        meta: bool = False
        if _MODIFIER_SEQUENCE.fullmatch(event):
            params: list[str] = event[2:-1].split(";")
            param1: str = params[0]
            modifier: int = int(params[1]) - 1
            shift = shift or modifier & 0x01 == 0x01
            alt = alt or modifier & 0x02 == 0x02
            ctrl = ctrl or modifier & 0x04 == 0x04
            meta = meta or modifier & 0x08 == 0x08
            event = event[:2] + (param1 if param1 != "1" else "") + event[-1:]

        if event == "\x1b[Z":  # Handle shift+tab
            shift, event = True, "\t"

        button: int | None
        if _SGR_MOUSE_SEQUENCE.fullmatch(event):
            button = int(event[3:-1].split(";")[0])
        elif _MOUSE_SEQUENCE.fullmatch(event):
            button = ord(event[-3:-2]) - 0x20
        else:
            button = None

        if button is not None and button & 0xc3 in MOUSE_BUTTONS:
            shift = shift or button & 0x04 == 0x04
            alt = alt or button & 0x08 == 0x08
            ctrl = ctrl or button & 0x10 == 0x10
            event = MOUSE_BUTTONS[button & 0xc3]
        else:
            event = INPUT_EVENTS.get(event, event)

        self.shortcut: str = (
            ("ctrl+" if ctrl else "")
            + ("alt+" if alt else "")
            + ("shift+" if shift else "")
            + ("meta+" if meta else "")
            + (event.lower() if len(event) == 1 else event)
        )

    @property
    def moving(self) -> bool:
        """Is moving."""
        button: int
        if _MOUSE_SEQUENCE.fullmatch(self):
            button = ord(self[-3:-2]) - 0x20
        elif _SGR_MOUSE_SEQUENCE.fullmatch(self):
            button = int(self[:-1].partition("<")[2].split(";")[0])
        else:
            return False

        return button & 0x20 == 0x20

    @property
    def pressed(self) -> bool:
        """Is key pressed."""
        button: int
        if _MOUSE_SEQUENCE.fullmatch(self):
            button = ord(self[-3:-2]) - 0x20
        elif _SGR_MOUSE_SEQUENCE.fullmatch(self):
            button = int(self[:-1].partition("<")[2].split(";")[0])
            if self.endswith("m"):
                return False
        else:
            return True

        return MOUSE_BUTTONS.get(button & 0xc3) != "no_button"


def _get_ss3_sequence(*, timeout: float | None = None) -> str:
    """Get SS3 sequence from command line."""
    char: str | None = _read_stdin_char(timeout=timeout)
    return char if char else ""


def _get_csi_sequence(*, timeout: float | None = None) -> str:
    """Get CSI sequence from command line."""
    csi_sequence: str = ""
    char: str | None = _read_stdin_char(timeout=timeout)
    if char is None:
        return csi_sequence

    if csi_sequence + char == "<":
        csi_sequence += char
        char = _read_stdin_char()

    while char in _PARAM_CHARS:
        csi_sequence += char
        char = _read_stdin_char()

    csi_sequence += char
    if csi_sequence == "t":
        csi_sequence += _read_stdin(2)

    if csi_sequence == "M":
        csi_sequence += _read_stdin(3)

    if csi_sequence == "T":
        csi_sequence += _read_stdin(6)

    return csi_sequence


# noinspection PyMissingOrEmptyDocstring
@overload
def get_input_event(*, timeout: None = None) -> InputEvent:
    ...


# noinspection PyMissingOrEmptyDocstring
@overload
def get_input_event(*, timeout: float = ...) -> InputEvent | None:
    ...


def get_input_event(*, timeout: float | None = None) -> InputEvent | None:
    """Get input event from command line."""
    key: str | None = _read_stdin_char(timeout=timeout, unicode=True)
    if key is None:
        return key

    if key != "\x1b":
        return InputEvent(key)

    char: str | None = _read_stdin_char(timeout=_TIMEOUT, unicode=True)
    if not char:
        return InputEvent(key)

    key += char
    if key == "\x1bO":
        key += _get_ss3_sequence(timeout=_TIMEOUT)
    elif key == "\x1b[":
        key += _get_csi_sequence(timeout=_TIMEOUT)
    elif key == "\x1b\x1b":
        char = _read_stdin_char(timeout=_TIMEOUT)
        if not char:
            return InputEvent(key)

        key += char
        if key == "\x1b\x1bO":
            key += _get_ss3_sequence()
        elif key == "\x1b\x1b[":
            key += _get_csi_sequence()

    return InputEvent(key)
