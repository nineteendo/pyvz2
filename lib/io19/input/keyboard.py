"""19.io helper functions for keyboard input."""
# Linting arguments
# mypy: disable-error-code=attr-defined
# pylint: disable=useless-suppression
# ...
# pylint: disable=import-error, too-few-public-methods, too-many-branches

# Standard libraries
import signal
from platform import system
from queue import Queue
from re import search
from signal import SIG_DFL, SIGINT, raise_signal
from signal import signal as set_signal_handler
from sys import stdin
from threading import Thread
from types import FrameType
from typing import Optional, Union, overload

__all__: list[str] = ['UNPRINTABLE']
__all__ += [
    'CtrlCodes', 'CtrlSequences', 'Event',  'KeyReader', 'MouseButtons',
    'RawInput', 'UserInput'
]
__all__ += ['read_event', 'suspend', 'is_printable']
_CSI: str = '\x1b['
_CSI_CHAR: bytes = b'\x1b['
_CSI_CHARS: bytes = b'0123456789;'
_END_OF_MEDIUM_CHAR: bytes = b'\x19'
_END_OF_TEXT_CHAR: bytes = b'\x03'
_ESC_CHAR: bytes = b'\x1b'
_ESC_CSI_CHAR: bytes = b'\x1b\x1b['
_ESC_ESC_CHAR: bytes = b'\x1b\x1b'
_ESC_O_CHAR: bytes = b'\x1bO'
_IFLAG: int = 0
_SUBSTITUTE_CHAR: bytes = b'\x1a'

UNPRINTABLE: str = r'[\0-\x1f\x7f-\x9f]'


def is_printable(string: str) -> bool:
    """Return if character is printable."""
    return not search(UNPRINTABLE, string)


class CtrlCodes:
    """
    Class for C0, C1, C8 & C9 controls.

    All these characters are considered unprintable
    """

    NULL:                                     str = '\0'
    START_OF_HEADING:                         str = '\x01'  # Ctrl+A, Cmd+Left
    START_OF_TEXT:                            str = '\x02'  # Ctrl+B
    END_OF_TEXT:                              str = '\x03'  # Ctrl+C
    END_OF_TRANSMISSION:                      str = '\x04'  # Ctrl+D
    ENQUIRY:                                  str = '\x05'  # Ctrl+E, Cmd+Right
    ACKNOWLEDGE:                              str = '\x06'  # Ctrl+F
    BELL:                                     str = '\a'    # Ctrl+G
    BACKSPACE:                                str = '\b'    # Ctrl+H
    HORIZONTAL_TABULATION:                    str = '\t'    # Ctrl+I, Tab
    LINE_FEED:                                str = '\n'    # Ctrl+J, Enter
    VERTICAL_TABULATION:                      str = '\v'    # Ctrl+K
    FORM_FEED:                                str = '\f'    # Ctrl+L
    CARRIAGE_RETURN:                          str = '\r'    # Ctrl+M, Enter
    SHIFT_OUT:                                str = '\x0e'  # Ctrl+N
    SHIFT_IN:                                 str = '\x0f'  # Ctrl+O
    DATA_LINK_ESCAPE:                         str = '\x10'  # Ctrl+P
    XON:                                      str = '\x11'  # Ctrl+Q
    DEVICE_CONTROL_TWO:                       str = '\x12'  # Ctrl+R
    XOFF:                                     str = '\x13'  # Ctrl+S
    DEVICE_CONTROL_FOUR:                      str = '\x14'  # Ctrl+T
    NEGATIVE_ACKNOWLEDGE:                     str = '\x15'  # Ctrl+U
    SYNCHRONOUS_IDLE:                         str = '\x16'  # Ctrl+V
    END_OF_TRANSMISSION_BLOCK:                str = '\x17'  # Ctrl+W
    CANCEL:                                   str = '\x18'  # Ctrl+X
    END_OF_MEDIUM:                            str = '\x19'  # Ctrl+Y
    SUBSTITUTE:                               str = '\x1a'  # Ctrl+Z
    ESCAPE:                                   str = '\x1b'  # Esc
    FILE_SEPARATOR:                           str = '\x1c'
    GROUP_SEPARATOR:                          str = '\x1d'
    RECORD_SEPARATOR:                         str = '\x1e'
    UNIT_SEPARATOR:                           str = '\x1f'
    DELETE:                                   str = '\x7f'  # Backspace
    PADDING_CHARACTER:                        str = '\x80'
    HIGH_OCTET_PRESET:                        str = '\x81'
    BREAK_PERMITTED_HERE:                     str = '\x82'
    NO_BREAK_HERE:                            str = '\x83'
    INDEX:                                    str = '\x84'
    NEXT_LINE:                                str = '\x85'
    START_OF_SELECTED_AREA:                   str = '\x86'
    END_OF_SELECTED_AREA:                     str = '\x87'
    HORIZONTAL_TABULATION_SET:                str = '\x88'
    HORIZONTAL_TABULATION_WITH_JUSTIFICATION: str = '\x89'
    LINE_TABULATION_SET:                      str = '\x8a'
    PARTIAL_LINE_DOWN:                        str = '\x8b'
    PARTIAL_LINE_UP:                          str = '\x8c'
    REVERSE_INDEX:                            str = '\x8d'
    SINGLE_SHIFT_TWO:                         str = '\x8e'
    SINGLE_SHIFT_THREE:                       str = '\x8f'
    DEVICE_CONTROL_STRING:                    str = '\x90'
    PRIVATE_USE_ONE:                          str = '\x91'
    PRIVATE_USE_TWO:                          str = '\x92'
    SET_TRANSMIT_STATE:                       str = '\x93'
    CANCEL_CHARACTER:                         str = '\x94'
    MESSAGE_WAITING:                          str = '\x95'
    START_OF_PROTECTED_AREA:                  str = '\x96'
    END_OF_PROTECTED_AREA:                    str = '\x97'
    START_OF_STRING:                          str = '\x98'
    SINGLE_GRAPHIC_CHARACTER_INTRODUCER:      str = '\x99'
    SINGLE_CHARACTER_INTRODUCER:              str = '\x9a'
    CONTROL_SEQUENCE_INTRODUCER:              str = '\x9b'
    STRING_TERMINATOR:                        str = '\x9c'
    OPERATING_SYSTEM_COMMAND:                 str = '\x9d'
    PRIVATE_MESSAGE:                          str = '\x9e'
    APPLICATION_PROGRAM_COMMAND:              str = '\x9f'


class CtrlSequences:
    """Class for control sequences."""

    ESC:            str = '\x1b'
    CSI:            str = f'{ESC}['
    MOUSE:          str = f'{CSI}<'     # Mouse
    UP:             str = f'{CSI}A'     # Up
    DOWN:           str = f'{CSI}B'     # Down
    RIGHT:          str = f'{CSI}C'     # Right
    LEFT:           str = f'{CSI}D'     # Left
    SHIFT_TAB:      str = f'{CSI}Z'     # Shift+Tab
    CONTROL_HOME:   str = f'{CSI}1;5H'  # Ctrl+Home
    DELETE:         str = f'{CSI}3~'    # Delete
    META_A:         str = f'{ESC}a'     # Meta+A
    META_B:         str = f'{ESC}b'     # Meta+B, Meta+Left
    META_C:         str = f'{ESC}c'     # Meta+C
    META_D:         str = f'{ESC}d'     # Meta+D
    META_E:         str = f'{ESC}e'     # Meta+E
    META_F:         str = f'{ESC}f'     # Meta+F, Meta+Right
    META_G:         str = f'{ESC}g'     # Meta+G
    META_H:         str = f'{ESC}h'     # Meta+H
    META_I:         str = f'{ESC}i'     # Meta+I
    META_J:         str = f'{ESC}j'     # Meta+J
    META_K:         str = f'{ESC}k'     # Meta+K
    META_L:         str = f'{ESC}l'     # Meta+L
    META_M:         str = f'{ESC}m'     # Meta+M
    META_N:         str = f'{ESC}n'     # Meta+N
    META_O:         str = f'{ESC}o'     # Meta+O
    META_P:         str = f'{ESC}p'     # Meta+P
    META_Q:         str = f'{ESC}q'     # Meta+Q
    META_R:         str = f'{ESC}r'     # Meta+R
    META_S:         str = f'{ESC}s'     # Meta+S
    META_T:         str = f'{ESC}t'     # Meta+T
    META_U:         str = f'{ESC}u'     # Meta+U
    META_V:         str = f'{ESC}v'     # Meta+V
    META_W:         str = f'{ESC}w'     # Meta+W
    META_X:         str = f'{ESC}x'     # Meta+X
    META_Y:         str = f'{ESC}y'     # Meta+Y
    META_Z:         str = f'{ESC}z'     # Meta+Z
    META_BACKSPACE: str = f'{ESC}\x7f'  # Meta+Backspace


class MouseButtons:
    """Class for mouse buttons."""

    L:                 str = '0'
    M:                 str = '1'
    R:                 str = '2'
    SHIFT_L:           str = '4'
    SHIFT_M:           str = '5'
    SHIFT_R:           str = '6'
    META_L:            str = '8'
    META_M:            str = '9'
    META_R:            str = '10'
    META_SHIFT_L:      str = '12'
    META_SHIFT_M:      str = '13'
    META_SHIFT_R:      str = '14'
    CTRL_L:            str = '16'
    CTRL_M:            str = '17'
    CTRL_R:            str = '18'
    CTRL_SHIFT_L:      str = '20'
    CTRL_SHIFT_M:      str = '21'
    CTRL_SHIFT_R:      str = '22'
    CTRL_META_L:       str = '24'
    CTRL_META_M:       str = '25'
    CTRL_META_R:       str = '26'
    CTRL_META_SHIFT_L: str = '28'
    CTRL_META_SHIFT_M: str = '29'
    CTRL_META_SHIFT_R: str = '30'
    B:                 str = '64'
    F:                 str = '65'
    SHIFT_B:           str = '68'
    SHIFT_F:           str = '69'
    META_B:            str = '72'
    META_F:            str = '73'
    META_SHIFT_B:      str = '76'
    META_SHIFT_F:      str = '77'
    CTRL_B:            str = '80'
    CTRL_F:            str = '81'
    CTRL_SHIFT_B:      str = '84'
    CTRL_SHIFT_F:      str = '85'
    CTRL_META_B:       str = '88'
    CTRL_META_F:       str = '89'
    CTRL_META_SHIFT_B: str = '92'
    CTRL_META_SHIFT_F: str = '93'


RawInput: Union[type['_WinRawInput'], type['_UnixRawInput']]
if system() == 'Windows':
    from ctypes import byref, c_ulong, windll
    # noinspection PyCompatibility
    from msvcrt import get_osfhandle  # NOTE - Windows module

    class _WinRawInput:
        """Class to enable & re-enable raw input."""

        old: c_ulong = c_ulong()
        windll.kernel32.GetConsoleMode(
            get_osfhandle(stdin.fileno()), byref(old)
        )

        @staticmethod
        def enable() -> None:
            """Enable raw input."""
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdin.fileno()),
                0x0200 | 0x0100 | 0x0080 | 0x0040 | 0x0020 | 0x0010
                # 0x0001 -> disabled, because 0x0002 is disabled
                # 0x0002 -> disabled, to read character by character
                # 0x0004 -> disabled, because 0x0002 is disabled
                # 0x0200 -> enabled, to work with unix escape sequences
            )
            print(end=f'{_CSI}?1000h{_CSI}?1006h', flush=True)

        @classmethod
        def disable(cls) -> None:
            """Disable raw input."""
            windll.kernel32.SetConsoleMode(
                get_osfhandle(stdin.fileno()), cls.old.value
            )
            print(end=f'{_CSI}?1000l{_CSI}?1006l', flush=True)

    RawInput = _WinRawInput
elif system() in ['Darwin', 'Linux']:
    from termios import ICRNL, IXON, TCSANOW, tcgetattr, tcsetattr
    from tty import setcbreak

    class _UnixRawInput:
        """Class to enable & re-enable raw input."""

        old_value: list[Union[int, list[Union[bytes, int]]]] = tcgetattr(stdin)

        @staticmethod
        def enable() -> None:
            """Enable raw input."""
            mode: list = tcgetattr(stdin)
            mode[_IFLAG] &= ~(ICRNL | IXON)
            tcsetattr(stdin, TCSANOW, mode)
            setcbreak(stdin, TCSANOW)
            print(end=f'{_CSI}?1000h{_CSI}?1006h', flush=True)

        @classmethod
        def disable(cls) -> None:
            """Disable raw input."""
            tcsetattr(stdin, TCSANOW, cls.old_value)
            print(end=f'{_CSI}?1000l{_CSI}?1006l', flush=True)

    RawInput = _UnixRawInput
else:
    raise RuntimeError(f'Unsupported operating system: {system()!r}')


class KeyReader:
    """Class to read keys from standard input."""

    char: Optional[bytes] = None
    thread: Optional[Thread] = None

    @classmethod
    def read(cls, *, number: int = 1) -> bytes:
        """Read characters from standard input (default 1)."""
        result: bytes = b''
        for _1 in range(number):
            result += cls.read_char()

        return result

    @classmethod
    @overload
    def read_char(cls, *, timeout: None = None) -> bytes:
        """Read character from standard input & store in cls.char."""

    @classmethod
    @overload
    def read_char(cls, *, timeout: float = ...) -> Optional[bytes]:
        """Read character from standard input & store in cls.char."""

    @classmethod
    def read_char(cls, *, timeout: Optional[float] = None) -> Optional[
        bytes
    ]:
        """Read character from standard input & store in cls.char."""
        while True:
            char: Optional[bytes]
            if cls.thread is not None and cls.thread.is_alive():
                cls.thread.join(timeout)
            elif timeout is None:
                cls.read_from_stdin()
            else:
                cls.thread = Thread(
                    target=cls.read_from_stdin, daemon=True
                )
                cls.thread.start()
                cls.thread.join(timeout)

            char = cls.char
            if char is None:
                return char

            if char == _END_OF_TEXT_CHAR:
                # NOTE - Parity, KeyboardInterrupt terminates Python on Mac
                raise_signal(SIGINT)
            elif char in [b'', _END_OF_MEDIUM_CHAR, _SUBSTITUTE_CHAR]:
                # NOTE - Parity, Ctrl-Y & Ctrl-Z suspends Python on Mac
                raise_signal(getattr(signal, 'SIGTSTP', SIGINT))
            else:
                return char

    @classmethod
    def read_from_stdin(cls) -> None:
        """Read character from standard input & store in cls.char."""
        cls.char = None
        cls.char = stdin.buffer.read(1)


class Event:
    """Class to represent events."""

    queue: Queue = Queue()

    def __init__(
        self, *, button: str = '', col: str = '', pressed: bool = True,
        row: str = '', special: str = '', text: str = ''
    ) -> None:
        """Make new Event instance."""
        self.button: str = button
        self.col: str = col
        self.pressed: bool = pressed
        self.row: str = row
        self.special: str = special
        self.text: str = text

    def __repr__(self) -> str:
        """Get representation of Event."""
        return (
            f'Event(button={self.button!r}, col={self.col!r}, pressed=' +
            f'{self.pressed}, row={self.row!r}, special={self.special!r}, ' +
            f'text={self.text!r})'
        )

    @property
    def button_down(self) -> str:
        """Get button if pressed."""
        return self.button if self.pressed else ''

    @property
    def button_up(self) -> str:
        """Get button if released."""
        return '' if self.pressed else self.button

    @property
    def special_lower(self) -> str:
        """Lower special key."""
        return self.special.lower()


class UserInput(Event):
    """Class to read user input."""

    TIMEOUT_SECONDS: float = 0.01

    def __init__(self) -> None:  # noqa: MC0001
        """Make new UserInput instance."""
        super().__init__()
        key: bytes = KeyReader.read()
        key_ord: int = ord(key)
        if key == _ESC_CHAR:
            char: Optional[bytes] = KeyReader.read_char(
                timeout=self.TIMEOUT_SECONDS
            )
            if char is None:
                self.special = key.decode()
                return

            key += char
            if key == _ESC_ESC_CHAR:
                key += KeyReader.read()

            if key in [_CSI_CHAR, _ESC_CSI_CHAR]:
                pass
            elif key == _ESC_O_CHAR:
                self.special = (key + KeyReader.read()).decode()
                return
            else:
                self.special = key.decode()
                return

            char = KeyReader.read()
            while char in _CSI_CHARS:
                key += char
                char = KeyReader.read()

            self.special = (key + char).decode()
            if self.special != CtrlSequences.MOUSE:
                return

            mouse_info = b''
            char = KeyReader.read()
            while char in _CSI_CHARS:
                mouse_info += char
                char = KeyReader.read()

            self.button, self.col, self.row = mouse_info.decode().split(';')
            self.pressed = char == b'M'
        elif key_ord & 0x80 == 0:  # 0xxxxxxx
            decoded_key: str = key.decode()
            if is_printable(decoded_key):
                self.text = decoded_key
            else:
                self.special = decoded_key
        elif key_ord & 0xE0 == 0xC0:  # 110xxxxx10xxxxxx
            self.text = (key + KeyReader.read()).decode()
        elif key_ord & 0xF0 == 0xE0:  # 1110xxxx10xxxxxx10xxxxxx
            self.text = (key + KeyReader.read(number=2)).decode()
        elif key_ord & 0xF8 == 0xF0:  # 11110xxx10xxxxxx10xxxxxx10xxxxxx
            self.text = (key + KeyReader.read(number=3)).decode()
        else:
            raise RuntimeError(f'Read invalid character: {key!r}')


def read_event() -> None:
    """Add user input to Event.queue."""
    Event.queue.put(UserInput())


def suspend(signalnum: int = 0, _1: Optional[FrameType] = None) -> None:
    """Suspend execution."""
    RawInput.disable()
    set_signal_handler(signalnum, SIG_DFL)
    raise_signal(signalnum)
    set_signal_handler(signalnum, suspend)
