"""19.io classes & functions for dealing with bytes & str input."""
# FIXME - Alt + right click is disabled
# FIXME - Selecting text is disabled
# TODO - Separate thread to display text
# TODO - Remove signalnum logic
# TODO - Implement scrolling through too long text
# TODO - Cut off too long input
# TODO - Process long input in one go

# Linting arguments
# pylint: disable=useless-suppression
# ...
# pylint: disable=too-many-boolean-expressions, too-many-branches
# pylint: disable=too-many-instance-attributes, too-many-locals
# pylint: disable=too-many-statements

# Standard libraries
from abc import abstractmethod
from cmath import inf
from collections.abc import Callable
from os import get_terminal_size
from string import digits, punctuation, whitespace
from typing import Any, Literal, Optional, Union, overload

# Custom libraries
from ..output.ansi import erase_in_display, erase_in_line, set_cursor_position
from ..output.colors import bold, cyan, dim, green, red
from ..real2float import Real, format_real
from ..translate import gettext as _
from ._classes import VALUE, Representation
from ._input_event import BaseInputEvent
from .keyboard import (
    CtrlCodes, CtrlSequences, Event, MouseButtons, RawInput, is_printable,
    read_event
)

__all__: list[str] = ['BaseInputStr', 'BytesOrHex', 'InputBytes', 'InputStr']
__all__ += ['input_bytes', 'input_str']
_GROUP_SEPARATOR: str = ' '
_MAX_GROUP_SIZE: int = 48

BytesOrHex = Union[bytes, str]


class BaseInputStr(BaseInputEvent[VALUE]):
    """Base Input str."""

    def __init__(  # noqa: MC0001
        self, title: Any, *, allow_digits: bool = True,
        allow_punctuation: bool = True, allow_unicode: bool = True,
        allow_whitespace: bool = True, clear: bool = False, hide: bool = False,
        make_lowercase: bool = False, make_uppercase: bool = False,
        max_length: Real = inf, min_length: Real = 0, placeholder: str = '',
        representation: type[str] = Representation, value: Optional[str] = '',
        white_list: str = ''
    ) -> None:
        """Make new BaseInputStr instance."""
        if white_list:
            allow_digits = allow_punctuation = allow_unicode = True
            allow_whitespace, white_list = True, white_list.lower()
        elif not (allow_digits and allow_punctuation and allow_whitespace):
            allow_unicode = False

        clear = clear or hide
        if make_lowercase and make_uppercase:
            raise ValueError(
                'make_lowercase & make_uppercase are mutually exclusive'
            )

        if not (
            max_length == inf or isinstance(max_length, int) or
            max_length.is_integer()
        ):
            raise ValueError('max_length must be a whole number / inf')

        if not (isinstance(min_length, int) or min_length.is_integer()):
            raise ValueError('min_length must be a whole number')

        if not 0 <= min_length <= max_length <= inf:
            raise ValueError('min_length must lay between 0 & max_length')

        if value is None:
            value = ''
        elif not 0 <= len(value) <= max_length <= inf:
            raise ValueError('Value is longer than max_length')

        if not all(map(is_printable, white_list)):
            raise ValueError('Not all whitelist characters are printable')

        self.cursor_back: int = 0
        self.hide: bool = hide
        self.make_lowercase: bool = make_lowercase
        self.make_uppercase: bool = make_uppercase
        self.max_length: Real = max_length
        self.min_length: Real = min_length
        self.moved_back: int = 0
        self.placeholder: str = placeholder
        self.prevent_digits: bool = not allow_digits
        self.prevent_punctuation: bool = not allow_punctuation
        self.prevent_unicode: bool = not allow_unicode
        self.prevent_whitespace: bool = not allow_whitespace
        self.processed_input: str = ''
        self.suggestion_input: Optional[str] = None
        self.user_input: str = ''
        self.value: str = value
        self.white_list: str = white_list
        if not all(map(self.extend_user_input, self.value)):
            raise ValueError('Value is invalid')

        super().__init__(title, clear=clear, representation=representation)

    def process_input(self, user_input: str) -> Optional[str]:
        """Process user input, return display input."""
        return '*' * len(user_input) if self.hide else user_input

    def display_info(self) -> None:
        """Display additional info beside the title."""

    def validate_user_input(self, _1: str) -> Optional[str]:
        """Validate user input, return error message."""
        if len(self.user_input) < self.min_length:
            return _('Length is {0} too short').format(
                format_real(self.min_length - len(self.user_input), '')
            )

        return None

    def can_extend_user_input(self, _1: str, _2: str, _3: int) -> bool:
        """Can the user input be extended."""
        return True

    @overload
    def split_input(self, action: Literal[0]) -> tuple[str, str]:
        """Split input using no action."""

    @overload
    def split_input(self, action: Literal[-2]) -> None:
        """Split input using delete left."""

    @overload
    def split_input(self, action: Literal[-1]) -> None:
        """Split input using move left."""

    @overload
    def split_input(self, action: Literal[1]) -> None:
        """Split input using move right."""

    @overload
    def split_input(
        self, action: Literal[2], function: Callable[[str], str]
    ) -> None:
        """Split input using transform right."""

    @overload
    def split_input(self, action: Literal[3]) -> None:
        """Split input using delete right."""

    def split_input(  # noqa: MC0001
        self, action: Literal[-2, -1, 0, 1, 2, 3],
        function: Callable[[str], str] = str
    ) -> Optional[tuple[str, str]]:
        """Split input using action."""
        length: int = len(self.user_input)
        end: str = self.user_input[length - self.moved_back:]
        start: str = self.user_input[:length - self.moved_back]
        if not action:
            return start, end

        right: str
        if action < 0:
            right = ''
            while start.endswith(' '):
                right = start[-1:] + right
                start = start[:-1]

            while start and not start.endswith(' '):
                right = start[-1:] + right
                start = start[:-1]

            if action == -2:
                self.user_input = start + end
            else:
                self.moved_back = len(right + end)

            return None

        left: str = ''
        while action == 1 and end and not end.startswith(' '):
            left += end[:1]
            end = end[1:]

        while end.startswith(' '):
            left += end[:1]
            end = end[1:]

        right = ''
        while action >= 2 and end and not end.startswith(' '):
            right += end[:1]
            end = end[1:]

        self.moved_back = len(end)
        if action == 2:
            self.user_input = start + left + function(right) + end
        elif action == 3:
            self.user_input = start + end

        return None

    def extend_user_input(self, char: str) -> bool:
        """Extend user input."""
        length: int = len(self.user_input)
        end: str = self.user_input[length - self.moved_back:]
        start: str = self.user_input[:length - self.moved_back]
        if length >= self.max_length or (
            self.white_list and char.lower() not in self.white_list or
            char in digits and self.prevent_digits or
            char in punctuation and self.prevent_punctuation or
            not char.isascii() and self.prevent_unicode or
            char in whitespace and self.prevent_whitespace
        ) or not self.can_extend_user_input(
            self.user_input.lower(), char.lower(), self.moved_back
        ):
            return False

        # Valid text
        self.user_input = start
        if self.make_lowercase:
            self.user_input += char.lower()
        elif self.make_uppercase:
            self.user_input += char.upper()
        else:
            self.user_input += char

        self.user_input += end
        return True

    def handle_user_input(self, event: Event) -> bool:  # noqa: MC0001
        """Handle user input."""
        length: int = len(self.user_input)
        end: str
        start: str
        start, end = self.split_input(0)
        if event.special == CtrlCodes.START_OF_HEADING and (
            self.moved_back < length
        ):
            # Move cursor to start of line
            self.moved_back = length
        elif event.special in [
            CtrlCodes.START_OF_TEXT, CtrlSequences.LEFT
        ] and self.moved_back < length:
            # Move cursor back one character
            self.moved_back += 1
        elif event.special in [
            CtrlCodes.END_OF_TRANSMISSION, CtrlSequences.DELETE
        ] and self.moved_back:
            # Delete character after cursor
            self.user_input = start + end[1:]
            self.moved_back -= 1
        elif event.special == CtrlCodes.ENQUIRY and self.moved_back:
            # Move cursor to end of line
            self.moved_back = 0
        elif event.special in [
            CtrlCodes.ACKNOWLEDGE, CtrlSequences.RIGHT
        ] and self.moved_back:
            # Move cursor forward one character
            self.moved_back -= 1
        elif event.special in [
            CtrlCodes.DELETE, CtrlCodes.BACKSPACE
        ] and start:
            # Delete character before cursor
            self.user_input = start[:-1] + end
        elif event.special == CtrlCodes.HORIZONTAL_TABULATION and (
            self.suggestion_input is not None and
            self.user_input != self.suggestion_input
        ):
            # Complete input
            self.user_input = self.suggestion_input
        elif event.special == CtrlCodes.VERTICAL_TABULATION and end:
            # Delete everything after cursor
            self.moved_back, self.user_input = 0, start
        elif (
            event.special == CtrlCodes.FORM_FEED
            # or event.signalnum == getattr(signal, 'SIGWINCH', -1)
        ):
            # Clear screen
            set_cursor_position()
            self.cursor_position.move_back(self.cursor_position.chars)
        elif (
            event.special == CtrlCodes.DEVICE_CONTROL_TWO
            # or event.signalnum == getattr(signal, 'SIGALRM', -1)
        ):
            # Refresh screen
            pass
        elif event.special == CtrlCodes.DEVICE_CONTROL_FOUR and length >= 2:
            # Swap character before & after cursor
            moved_back: int = self.moved_back
            if not end:
                moved_back += 1
            elif not start:
                moved_back -= 1

            end = self.user_input[length - moved_back:]
            start = self.user_input[:length - moved_back]
            if not self.can_extend_user_input(
                (start + end[1:]).lower(), end[:1].lower(), moved_back
            ):
                return False  # Nothing changed

            self.user_input = start[:-1] + end[:1] + start[-1:] + end[1:]
            self.moved_back = moved_back - 1
        elif event.special in [
            CtrlSequences.CONTROL_HOME, CtrlCodes.NEGATIVE_ACKNOWLEDGE
        ] and start:
            # Delete everything before cursor
            self.user_input = end
        elif event.special in [
            CtrlCodes.END_OF_TRANSMISSION_BLOCK, CtrlSequences.META_BACKSPACE
        ] and start:
            # Delete word before cursor
            self.split_input(-2)
        elif event.special_lower in [
            CtrlCodes.ESCAPE, CtrlSequences.META_Q
        ] and self.user_input:
            # Delete whole line
            self.moved_back, self.user_input = 0, ''
        elif event.special_lower == CtrlSequences.META_B and start:
            # Move cursor back one word
            self.split_input(-1)
        elif event.special_lower == CtrlSequences.META_C and (
            end and not self.make_lowercase
        ):
            # Capitalize word after cursor
            self.split_input(2, str.capitalize)
        elif event.special_lower == CtrlSequences.META_D and end:
            # Delete word after cursor
            self.split_input(3)
        elif event.special_lower == CtrlSequences.META_F and end:
            # Move cursor forward one word
            self.split_input(1)
        elif event.special_lower == CtrlSequences.META_L and (
            end and not self.make_uppercase
        ):
            # Make word after cursor lowercase
            self.split_input(2, str.lower)
        elif event.special_lower == CtrlSequences.META_U and (
            end and not self.make_lowercase
        ):
            # Make word after cursor uppercase
            self.split_input(2, str.upper)
        elif event.special or not self.extend_user_input(event.text):
            return False

        return True

    @abstractmethod
    def submit(self) -> tuple[bool, Optional[VALUE]]:
        """Submit value as result."""

    def cleanup(self) -> None:
        """Clean up threads."""

    def get_value(self) -> Optional[VALUE]:  # noqa: MC0001
        """Get value."""
        RawInput.enable()
        while True:
            self.screen_width, self.screen_height = get_terminal_size()
            self.move_back(self.cursor_position.chars)
            self.cursor_position.width = self.screen_width
            title: str = self.get_title().replace('\n', ' ')
            if not self.placeholder:
                title = title[3 - self.screen_width:]
                self.cursor_position += 3 + len(title)
                print(green('?'), bold(title), end=' ')
            else:
                title += f' ({self.placeholder}) '
                title = title[3 - self.screen_width:]
                self.cursor_position += 2 + len(title)
                placeholder: str = title[-3 - len(self.placeholder):]
                title = title[:-4 - len(self.placeholder)]
                print(green('?'), bold(title), dim(placeholder), end='')
                self.placeholder = ''

            self.cursor_back = self.moved_back
            self.processed_input = self.user_input
            self.suggestion_input = None
            display_input: Optional[str] = self.process_input(self.user_input)
            error_message: Optional[str] = self.validate_user_input(
                self.processed_input
            )
            if display_input is None:
                display_input = self.user_input

            if self.suggestion_input is None:
                self.suggestion_input = self.processed_input

            self.display_info()
            self.cursor_position += 1 + len(self.processed_input)
            print(display_input, end=' ')
            if self.suggestion_input != self.user_input:
                self.cursor_position += 6
                self.cursor_back += 6
                print(dim('[Tab]'), end=' ')

            if error_message is not None:
                erase_in_line()
                print('\n' + red('>>'), error_message, end='')
                if self.cursor_position.col <= self.screen_width:
                    self.cursor_back += (
                        self.screen_width - self.cursor_position.col
                    )

                self.cursor_position.next_row()
                self.cursor_back += 3 + len(error_message)
                self.cursor_position += 3 + len(error_message)

            erase_in_display()
            self.move_back(1 + self.cursor_back)
            print(end='', flush=True)
            confirmed: bool = False
            read_event()
            event: Event = Event.queue.get_nowait()
            while not self.handle_user_input(event):
                if event.special == CtrlCodes.ESCAPE and not self.user_input:
                    # Cancel
                    confirmed = True
                    break

                if (event.button_down == MouseButtons.M or event.special in [
                    CtrlCodes.LINE_FEED, CtrlCodes.CARRIAGE_RETURN
                ]) and error_message is None:
                    # Submit input
                    break

                if event.pressed:
                    print(end=CtrlCodes.BELL, flush=True)

                read_event()
                event = Event.queue.get_nowait()
            else:
                continue

            result: Optional[VALUE]
            confirmed, result = (True, None) if confirmed else self.submit()
            if not confirmed:
                continue

            RawInput.disable()
            self.move_back(self.cursor_position.chars)
            self.cleanup()
            if self.clear or result is None:
                erase_in_display()
            else:
                print(
                    green('?'), bold(title), cyan(self.representation(result)),
                    end=''
                )
                erase_in_display()
                print()

            return result


class InputStr(BaseInputStr[str]):
    """Input str."""

    def submit(self) -> tuple[bool, Optional[str]]:
        """Submit value as result."""
        return True, self.processed_input


class InputBytes(BaseInputStr[bytes]):
    """Input bytes in hexadecimal."""

    def __init__(
        self, title: Any, *, clear: bool = False, group_size: int = 4,
        max_length: Real = inf, min_length: Real = 0,
        placeholder: Optional[str] = None,
        representation: type[str] = Representation,
        value: Optional[BytesOrHex] = ''
    ) -> None:
        """Make new InputBytes instance."""
        if not 0 <= group_size <= _MAX_GROUP_SIZE:
            raise ValueError(
                f'group_size must lay between 0 & {_MAX_GROUP_SIZE}'
            )

        self.group_size: int = 2 * group_size
        super().__init__(
            title, clear=clear, make_uppercase=True, max_length=2 * max_length,
            min_length=2 * min_length, placeholder=(
                _('Use hexadecimal digits') if placeholder is None else
                placeholder
            ), representation=representation,
            value=value.hex() if isinstance(value, bytes) else value,
            white_list=digits + 'abcdef'
        )

    def process_input(self, user_input: str) -> Optional[str]:
        """Process user input, return display input."""
        value: str = user_input
        if len(value) % 2:
            # Odd hex length
            value = value[:-1] + '0' + value[-1]
            self.cursor_back += 1 if self.moved_back else 0

        display_input: str
        self.suggestion_input = value
        if not self.group_size:
            self.processed_input = display_input = value
        elif len(_GROUP_SEPARATOR) != 1:
            raise RuntimeError(f'{_GROUP_SEPARATOR} must be 1 character')
        else:
            length: int = max(0, len(value) - 1)
            groups: list[str] = [
                value[i:i + self.group_size]
                for i in range(0, len(value), self.group_size)
            ]
            display_input = dim(_GROUP_SEPARATOR).join(groups)
            self.cursor_back += min(self.moved_back, length) // self.group_size
            self.processed_input = ' '.join(groups)

        if not len(user_input) % 2:
            # Even hex length
            return display_input

        # Odd hex length
        return display_input[:-2] + dim(0) + display_input[-1]

    def submit(self) -> tuple[bool, Optional[bytes]]:
        """Submit value as result."""
        return True, bytes.fromhex(self.processed_input)


def input_str(
    title: Any, *, allow_digits: bool = True, allow_punctuation: bool = True,
    allow_unicode: bool = True, allow_whitespace: bool = True,
    clear: bool = False, hide: bool = False, make_lowercase: bool = False,
    make_uppercase: bool = False, max_length: Real = inf, min_length: Real = 0,
    placeholder: str = '', representation: type[str] = Representation,
    value: Optional[str] = None, white_list: str = ''
) -> Optional[str]:
    """Read str from console input."""
    return InputStr(
        title, allow_digits=allow_digits, allow_punctuation=allow_punctuation,
        allow_unicode=allow_unicode, allow_whitespace=allow_whitespace,
        clear=clear, hide=hide, make_lowercase=make_lowercase,
        make_uppercase=make_uppercase, max_length=max_length,
        min_length=min_length, placeholder=placeholder,
        representation=representation, value=value, white_list=white_list
    ).get_value()


def input_bytes(
    title: Any, *, clear: bool = False, group_size: int = 4,
    max_length: Real = inf, min_length: Real = 0,
    placeholder: Optional[str] = None,
    representation: type[str] = Representation,
    value: Optional[BytesOrHex] = ''
) -> Optional[bytes]:
    """Read bytes from console input."""
    return InputBytes(
        title, clear=clear, group_size=group_size, max_length=max_length,
        min_length=min_length, placeholder=placeholder,
        representation=representation, value=value
    ).get_value()
