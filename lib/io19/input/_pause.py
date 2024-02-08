"""19.io classes & function for pausing."""
# FIXME: Selecting text is disabled

__all__: list[str] = [
    # PascalCase
    'BaseInputHandler', 'Pause',
    # snake_case
    'pause'
]

# Standard libraries
from abc import ABCMeta, abstractmethod
from gettext import gettext as _
from math import prod
from os import get_terminal_size, terminal_size
from sys import stdout
from typing import Generic, Optional

# Custom libraries
from ...colorized import (
    ColoredOutput, NoCursor, bold, cursor_up, erase_in_display, green,
    raw_print, red, set_cursor_position
)
from ...skiboard import Event, RawInput, get_event
from ._classes import VALUE, Cursor, Representation


class BaseInputHandler(Generic[VALUE], metaclass=ABCMeta):
    """Base class for handling console input."""

    def __init__(
        self, prompt: object = _('Press any key...'), *,
        representation: type[str] = Representation
    ) -> None:
        new_terminal_size:   terminal_size = get_terminal_size()
        self.cursor:         Cursor = Cursor(new_terminal_size.columns)
        self.prompt:         str = representation(prompt)
        self.representation: type[str] = representation
        self.terminal_size:  terminal_size = new_terminal_size

    def print_error(self, err: str) -> None:
        """Print error message."""
        columns: int = self.terminal_size.columns
        err_len: int = len(f'>> {err}')
        offset:  int = max(0, err_len - columns)
        if offset:
            err = '...' + err[offset+3:]

        raw_print(red('>>'), bold(err))
        self.cursor.wrote(f'? {err}')

    def print_prompt(self, msg: str = '', *, short: bool = False) -> None:
        """Print prompt."""
        self.clear_screen()
        max_chars: int = self.get_max_chars(short=short)
        if not max_chars:
            self.print_error(_('Enlarge window'))
            return

        prompt:     str = self.get_prompt()
        prompt_len: int = len(f'? {prompt}')
        offset:     int = max(
            0, prompt_len + min(len(msg), (max_chars + 1) // 2) - max_chars
        )
        if offset:
            prompt = '...' + prompt[offset+3:]

        raw_print(green('?'), bold(prompt))
        self.cursor.wrote(f'? {prompt}')

    def get_prompt(self) -> str:
        """Get prompt for user."""
        return self.prompt

    def get_max_chars(self, *, short: bool = False) -> int:
        """Get maximum characters."""
        if short:
            return prod(self.terminal_size)

        return prod(self.terminal_size) - self.terminal_size.columns

    @abstractmethod
    def get_value(self) -> Optional[VALUE]:
        """Get value from user."""

    def clear_screen(self) -> None:
        """Clear screen & reset cursor position."""
        new_terminal_size: terminal_size = get_terminal_size()
        if new_terminal_size != self.terminal_size:
            set_cursor_position()
        else:
            cursor_up(self.cursor.row)
            raw_print('\r')

        self.cursor = Cursor(new_terminal_size.columns)
        erase_in_display()
        self.terminal_size = new_terminal_size


class Pause(BaseInputHandler[None]):
    """Class for pausing."""

    @RawInput()
    @ColoredOutput()
    @NoCursor()
    def get_value(self) -> None:
        self.print_prompt(short=True)
        stdout.buffer.flush()
        event: Event = get_event()
        while not event.pressed:
            event = get_event()

        return self.clear_screen()


def pause(
    prompt: object = _('Press any key...'), *,
    representation: type[str] = Representation
) -> None:
    """Pause with message."""
    Pause(prompt, representation=representation).get_value()
