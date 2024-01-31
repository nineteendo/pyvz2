"""19.io helper functions for keyboard input."""
# Standard libraries
import re
import signal
import sys
from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from contextlib import ContextDecorator
from re import Pattern
from signal import SIGINT, raise_signal
from sys import stdin
from threading import Lock, Thread
from types import FrameType, TracebackType
from typing import Optional, Union, overload

__all__: list[str] = [
    'ADD', 'ALT', 'ALT_META', 'ALT_SHIFT', 'ALT_SHIFT_META', 'CTRL',
    'CTRL_ALT', 'CTRL_ALT_META', 'CTRL_ALT_SHIFT', 'CTRL_ALT_SHIFT_META',
    'CTRL_ESC', 'CTRL_META', 'CTRL_SHIFT', 'CTRL_SHIFT_META', 'ESC', 'ESC_ADD',
    'META', 'SHIFT', 'SHIFT_ADD', 'SHIFT_ESC', 'SHIFT_ESC_ADD', 'SHIFT_META',
    'UNPRINTABLE'
]
__all__ += [
    'CSISequences', 'CtrlCodes', 'Event', 'Modifier', 'Mouse', 'RawInput',
    'SS3Sequences'
]
__all__ += ['get_event']

_ADD_MODIFIABLE:   Pattern = re.compile(r'\x1b?[ -\x7f]')
_CSI_MODIFIABLE:   Pattern = re.compile(r'\x1b(O[P-S]|\[(\d+(;\d+)?)?[A-Z~])')
_CTRL_C:           bytes = b'\x03'
_CTRL_MODIFIABLE:  Pattern = re.compile(r'\x1b?[?-_a-z]')
_CTRL_Y:           bytes = b'\x19'
_CTRL_Z:           bytes = b'\x1a'
_EOF:              bytes = b''
_ESC_CSI:          str = '\x1b\x1b['
_ESC_MODIFIABLE:   Pattern = re.compile(r'.|\x1b[O\[].+')
_ESC_SS3:          str = '\x1b\x1bO'
_PARAM_CHARS:      str = '0123456789;'
_SHIFT_MODIFIABLE: Pattern = re.compile(r'\x1b?.')
_TIMEOUT:          float = 0.01

UNPRINTABLE: Pattern = re.compile(r'[\x00-\x1f\x7f-\x9f]')

Modifier = Callable[[str], 'Event']


class _Modifier:  # pylint: disable=too-few-public-methods
    """Class for modifiers."""

    def __init__(self, value: int) -> None:
        self.value: int = value & 0x3f

    def __call__(self, value: str) -> 'Event':
        """Add modifier to value."""
        if self.value & 0x01 and _SHIFT_MODIFIABLE.fullmatch(value):
            value = value.upper()

        if self.value & 0x04 and _CTRL_MODIFIABLE.fullmatch(value):
            value = value[:-1] + chr((ord(value[-1].upper()) - 0x40) % 0x80)

        if self.value & 0x0f and _CSI_MODIFIABLE.fullmatch(value):
            value = value.replace(SS3Sequences.SS3, CSISequences.CSI)
            start, _1, end = value[:-1].partition('[')
            params: list[str] = end.split(';')
            param1: int = int(params[0]) if params[0] else 1
            param2: int = int(params[1]) if len(params) > 1 else 1
            param2 = ((param2 - 1) | self.value & 0x0f) + 1
            value = f'{start}[{param1};{param2}{value[-1]}'

        if self.value & 0x10 and _ADD_MODIFIABLE.fullmatch(value):
            value = value[:-1] + chr(ord(value[-1]) + 0x80)

        if self.value & 0x20 and _ESC_MODIFIABLE.fullmatch(value):
            value = CtrlCodes.ESCAPE + value

        return Event(value)


SHIFT:               Modifier = _Modifier(0x01)
ALT:                 Modifier = _Modifier(0x02)
ALT_SHIFT:           Modifier = _Modifier(0x03)
CTRL:                Modifier = _Modifier(0x04)
CTRL_SHIFT:          Modifier = _Modifier(0x05)
CTRL_ALT:            Modifier = _Modifier(0x06)
CTRL_ALT_SHIFT:      Modifier = _Modifier(0x07)
META:                Modifier = _Modifier(0x08)
SHIFT_META:          Modifier = _Modifier(0x09)
ALT_META:            Modifier = _Modifier(0x0a)
ALT_SHIFT_META:      Modifier = _Modifier(0x0b)
CTRL_META:           Modifier = _Modifier(0x0c)
CTRL_SHIFT_META:     Modifier = _Modifier(0x0d)
CTRL_ALT_META:       Modifier = _Modifier(0x0e)
CTRL_ALT_SHIFT_META: Modifier = _Modifier(0x0f)
ADD:                 Modifier = _Modifier(0x10)
SHIFT_ADD:           Modifier = _Modifier(0x11)
ESC:                 Modifier = _Modifier(0x20)
SHIFT_ESC:           Modifier = _Modifier(0x21)
CTRL_ESC:            Modifier = _Modifier(0x24)
ESC_ADD:             Modifier = _Modifier(0x30)
SHIFT_ESC_ADD:       Modifier = _Modifier(0x31)


class CtrlCodes:  # pylint: disable=too-few-public-methods
    """Class for C0 control codes."""

    NULL:                      str = '\0'

    START_OF_HEADING:          str = '\x01'
    START_OF_TEXT:             str = '\x02'
    END_OF_TEXT:               str = '\x03'
    END_OF_TRANSMISSION:       str = '\x04'
    ENQUIRY:                   str = '\x05'
    ACKNOWLEDGE:               str = '\x06'

    BELL:                      str = '\a'
    BACKSPACE:                 str = '\b'
    HORIZONTAL_TABULATION:     str = '\t'
    LINE_FEED:                 str = '\n'
    VERTICAL_TABULATION:       str = '\v'
    FORM_FEED:                 str = '\f'
    CARRIAGE_RETURN:           str = '\r'

    SHIFT_OUT:                 str = '\x0e'
    SHIFT_IN:                  str = '\x0f'
    DATA_LINK_ESCAPE:          str = '\x10'
    XON:                       str = '\x11'
    DEVICE_CONTROL_TWO:        str = '\x12'
    XOFF:                      str = '\x13'
    DEVICE_CONTROL_FOUR:       str = '\x14'
    NEGATIVE_ACKNOWLEDGE:      str = '\x15'
    SYNCHRONOUS_IDLE:          str = '\x16'
    END_OF_TRANSMISSION_BLOCK: str = '\x17'
    CANCEL:                    str = '\x18'
    END_OF_MEDIUM:             str = '\x19'
    SUBSTITUTE:                str = '\x1a'

    ESCAPE:                    str = '\x1b'

    FILE_SEPARATOR:            str = '\x1c'
    GROUP_SEPARATOR:           str = '\x1d'
    RECORD_SEPARATOR:          str = '\x1e'
    UNIT_SEPARATOR:            str = '\x1f'
    DELETE:                    str = '\x7f'


class SS3Sequences:  # pylint: disable=too-few-public-methods
    """Class for SS3 sequences."""
    SS3:             str = '\x1bO'

    UP:              str = '\x1bOA'
    DOWN:            str = '\x1bOB'
    RIGHT:           str = '\x1bOC'
    LEFT:            str = '\x1bOD'
    END:             str = '\x1bOF'
    HOME:            str = '\x1bOH'

    KEYPAD_ENTER:    str = '\x1bOM'

    F1:              str = '\x1bOP'
    F2:              str = '\x1bOQ'
    F3:              str = '\x1bOR'
    F4:              str = '\x1bOS'

    KEYPAD_EQUALS:   str = '\x1bOX'
    KEYPAD_MULTIPLY: str = '\x1bOj'
    KEYPAD_ADD:      str = '\x1bOk'
    KEYPAD_COMMA:    str = '\x1bOl'
    KEYPAD_MINUS:    str = '\x1bOm'
    KEYPAD_PERIOD:   str = '\x1bOn'
    KEYPAD_DIVIDE:   str = '\x1bOo'

    KEYPAD_0:        str = '\x1bOp'
    KEYPAD_1:        str = '\x1bOq'
    KEYPAD_2:        str = '\x1bOr'
    KEYPAD_3:        str = '\x1bOs'
    KEYPAD_4:        str = '\x1bOt'
    KEYPAD_5:        str = '\x1bOu'
    KEYPAD_6:        str = '\x1bOv'
    KEYPAD_7:        str = '\x1bOw'
    KEYPAD_8:        str = '\x1bOx'
    KEYPAD_9:        str = '\x1bOy'


class CSISequences:  # pylint: disable=too-few-public-methods
    """Class for CSI sequences."""
    CSI:         str = '\x1b['

    SGR_MOUSE:   str = '\x1b[<'
    UP:          str = '\x1b[A'
    DOWN:        str = '\x1b[B'
    RIGHT:       str = '\x1b[C'
    LEFT:        str = '\x1b[D'
    BEGIN:       str = '\x1b[E'
    END:         str = '\x1b[F'
    NEXT:        str = '\x1b[G'
    HOME:        str = '\x1b[H'
    # INSERT:    str = '\x1b[L'
    MOUSE:       str = '\x1b[M'
    MOUSE_MOVE:  str = '\x1b[T'
    SHIFT_TAB:   str = '\x1b[Z'
    MOUSE_CLICK: str = '\x1b[t'
    # HOME:      str = '\x1b[1~'
    INSERT:      str = '\x1b[2~'
    DELETE:      str = '\x1b[3~'
    # END:       str = '\x1b[4~'
    PAGE_UP:     str = '\x1b[5~'
    PAGE_DOWN:   str = '\x1b[6~'

    F5:          str = '\x1b[15~'
    F6:          str = '\x1b[17~'
    F7:          str = '\x1b[18~'
    F8:          str = '\x1b[19~'
    F9:          str = '\x1b[20~'
    F10:         str = '\x1b[21~'
    F11:         str = '\x1b[23~'
    F12:         str = '\x1b[24~'
    F13:         str = '\x1b[25~'
    F14:         str = '\x1b[26~'
    F15:         str = '\x1b[28~'
    F16:         str = '\x1b[29~'
    F17:         str = '\x1b[31~'
    F18:         str = '\x1b[32~'
    F19:         str = '\x1b[33~'
    F20:         str = '\x1b[34~'


class Mouse:  # pylint: disable=too-few-public-methods
    """Class for mouse buttons."""
    BUTTON_1:       int = 0x00
    BUTTON_2:       int = 0x01
    BUTTON_3:       int = 0x02
    RELEASE:        int = 0x03

    SHIFT:          int = 0x04
    ALT:            int = 0x08
    ALT_SHIFT:      int = 0x0c
    CTRL:           int = 0x10
    CTRL_SHIFT:     int = 0x14
    CTRL_ALT:       int = 0x18
    CTRL_ALT_SHIFT: int = 0x1c

    BUTTON_4:       int = 0x40
    BUTTON_5:       int = 0x41
    BUTTON_6:       int = 0x42
    BUTTON_7:       int = 0x43

    BUTTON_8:       int = 0x80
    BUTTON_9:       int = 0x81
    BUTTON_10:      int = 0x82
    BUTTON_11:      int = 0x83


class _BaseRawInput(ContextDecorator, metaclass=ABCMeta):
    """Base class for raw input."""
    count: int = 0

    def __enter__(self) -> None:
        _BaseRawInput.count += 1
        self.enable()

    def __exit__(
        self, _1: Optional[type[BaseException]], _2: Optional[BaseException],
        _3: Optional[TracebackType]
    ) -> None:
        _BaseRawInput.count = max(0, _BaseRawInput.count - 1)
        if not _BaseRawInput.count:
            self.disable()

    @classmethod
    @abstractmethod
    def disable(cls) -> None:
        """Disable raw input."""

    @staticmethod
    @abstractmethod
    def enable() -> None:
        """Enable raw input."""


if sys.platform == "win32":
    from ctypes import byref, c_ulong, windll
    # noinspection PyCompatibility
    from msvcrt import get_osfhandle  # pylint: disable=import-error

    class RawInput(_BaseRawInput):
        """Class to enable & re-enable raw input."""
        old: c_ulong = c_ulong()
        windll.kernel32.GetConsoleMode(
            get_osfhandle(stdin.fileno()), byref(old)
        )

        @classmethod
        def disable(cls) -> None:
            print(end='\x1b[?1000l\x1b[?1006l', flush=True)
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdin.fileno()), cls.old.value
            )

        @staticmethod
        def enable() -> None:
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdin.fileno()),
                0x0200 | 0x0100 | 0x0080 | 0x0040 | 0x0020 | 0x0010
                # 0x0001 -> disabled, because 0x0002 is disabled
                # 0x0002 -> disabled, to read character by character
                # 0x0004 -> disabled, because 0x0002 is disabled
                # 0x0200 -> enabled, to work with unix escape sequences
            )
            print(end='\x1b[?1000h\x1b[?1006h', flush=True)
# pylint: disable=consider-using-in
elif sys.platform == 'darwin' or sys.platform == 'linux':
    # pylint: disable=ungrouped-imports, import-error
    from signal import SIG_DFL, SIGTSTP  # pylint: disable=no-name-in-module
    from termios import ICRNL, IXON, TCSANOW, tcgetattr, tcsetattr
    from tty import setcbreak

    _IFLAG: int = 0

    class RawInput(_BaseRawInput):
        """Class to enable & re-enable raw input."""
        old_value: list[Union[int, list[Union[bytes, int]]]] = tcgetattr(stdin)

        @classmethod
        def disable(cls) -> None:
            tcsetattr(stdin, TCSANOW, cls.old_value)
            print(end='\x1b[?1000l\x1b[?1006l', flush=True)

        @staticmethod
        def enable() -> None:
            print(end='\x1b[?1000h\x1b[?1006h', flush=True)
            mode: list = tcgetattr(stdin)
            mode[_IFLAG] &= ~(ICRNL | IXON)
            tcsetattr(stdin, TCSANOW, mode)
            setcbreak(stdin, TCSANOW)

        @classmethod
        def resume(cls, _1: int, _2: Optional[FrameType]):
            """Resume raw input."""
            signal.signal(SIGTSTP, cls.suspend)
            if _BaseRawInput.count:
                cls.enable()

        @classmethod
        def suspend(cls, _1: int, _2: Optional[FrameType]):
            """Suspend raw input."""
            cls.disable()
            signal.signal(SIGTSTP, SIG_DFL)
            raise_signal(SIGTSTP)
else:
    raise RuntimeError(f'Unsupported platform: {sys.platform!r}')


class _KeyReader:
    """Class to read keys from standard input."""

    byte:   Optional[bytes] = None
    lock:   Lock = Lock()
    thread: Optional[Thread] = None

    @classmethod
    def read(cls, number: int, *, raw: bool = False) -> str:
        """Read from standard input."""
        result: str = ''
        for _1 in range(number):
            result += cls.read_char(raw=raw)

        return result

    @classmethod
    @overload
    def read_char(cls, *, raw: bool = False, timeout: None = None) -> str:
        """Read character from standard input."""

    @classmethod
    @overload
    def read_char(
        cls, *, raw: bool = False, timeout: float = ...
    ) -> Optional[str]:
        """Read character from standard input."""

    @classmethod
    def read_char(
        cls, *, raw: bool = False, timeout: Optional[float] = None
    ) -> Optional[str]:
        """Read character from standard input."""
        # NOTE - We need to read bytes because of bug on Windows
        byte: Optional[bytes] = cls.read_byte(timeout=timeout)
        if byte is None:
            return byte

        if byte == _CTRL_C:
            # NOTE - Parity, KeyboardInterrupt terminates Python on macOS
            raise_signal(SIGINT)

        if byte in [_CTRL_Y, _CTRL_Z, _EOF]:
            # NOTE - Parity, Ctrl-Y & Ctrl-Z suspends Python on macOS
            raise_signal(getattr(signal, 'SIGTSTP', SIGINT))

        if raw:
            return byte.decode('latin_1')

        # Handle multi-byte characters
        byte_ord: int = ord(byte)
        if byte_ord & 0xC0 == 0xC0:  # 11xxxxxx10xxxxxx...
            byte += cls.read_byte()

        if byte_ord & 0xE0 == 0xE0:  # 111xxxxx10xxxxxx10xxxxxx...
            byte += cls.read_byte()

        if byte_ord & 0xF0 == 0xF0:  # 1111xxxx10xxxxxx10xxxxxx10xxxxxx...
            byte += cls.read_byte()

        if byte_ord & 0xF8 == 0xF8:  # 11111xxx
            raise RuntimeError(f'Read invalid character: {byte!r}')

        return byte.decode()

    @classmethod
    @overload
    def read_byte(cls, *, timeout: None = None) -> bytes:
        """Read byte from standard input."""

    @classmethod
    @overload
    def read_byte(cls, *, timeout: float = ...) -> Optional[bytes]:
        """Read byte from standard input."""

    @classmethod
    def read_byte(cls, *, timeout: Optional[float] = None) -> Optional[
        bytes
    ]:
        """Read byte from standard input."""
        while True:
            if cls.thread is not None and cls.thread.is_alive():
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
        byte: Optional[bytes] = stdin.buffer.read(1)  # Don't lock before read
        with cls.lock:
            cls.byte = byte


class Event(str):
    """Class to represent events."""

    @property
    def button(self) -> Optional[int]:
        """Mouse button."""
        if self.startswith(
            (ESC(CSISequences.SGR_MOUSE), CSISequences.SGR_MOUSE)
        ):
            return int(self[:-1].partition('<')[2].split(';')[0])

        if self.startswith((ESC(CSISequences.MOUSE), CSISequences.MOUSE)):
            return ord(self[-3:-2]) - 32

        return None

    def ispressed(self) -> bool:
        """Is key pressed."""
        if self.startswith(
            (ESC(CSISequences.SGR_MOUSE), CSISequences.SGR_MOUSE)
        ):
            return self.endswith('M')

        if self.startswith((ESC(CSISequences.MOUSE), CSISequences.MOUSE)):
            return ord(self[-3:-2]) - 32 & 0x03 != Mouse.RELEASE

        return True


def get_event() -> 'Event':  # pylint: disable=too-many-return-statements
    """Get event from console."""
    key: str = _KeyReader.read_char()
    if key != CtrlCodes.ESCAPE:
        return Event(key)

    char: Optional[str] = _KeyReader.read_char(timeout=_TIMEOUT)
    if char is None:
        return Event(key)

    key += char
    if key not in [ESC(CtrlCodes.ESCAPE), ESC('O'), ESC('[')]:
        return Event(key)

    char = _KeyReader.read_char(raw=True, timeout=_TIMEOUT)
    if char is None:
        return Event(key)

    if key == ESC(CtrlCodes.ESCAPE):
        key += char
        if key not in [_ESC_SS3, _ESC_CSI]:
            return Event(key)

        char = _KeyReader.read_char(raw=True)

    if key in [_ESC_SS3, SS3Sequences.SS3]:
        return Event(key + char)

    if key + char in (ESC(CSISequences.MOUSE_CLICK), CSISequences.MOUSE_CLICK):
        return Event(key + char + _KeyReader.read(2, raw=True))

    if key + char in (ESC(CSISequences.MOUSE), CSISequences.MOUSE):
        return Event(key + char + _KeyReader.read(3, raw=True))

    if key + char in (ESC(CSISequences.MOUSE_MOVE), CSISequences.MOUSE_MOVE):
        return Event(key + char + _KeyReader.read(6, raw=True))

    if key + char in (ESC(CSISequences.SGR_MOUSE), CSISequences.SGR_MOUSE):
        key += char
        char = _KeyReader.read_char(raw=True)

    while char in _PARAM_CHARS:
        key += char
        char = _KeyReader.read_char(raw=True)

    key += char
    return Event(key)
