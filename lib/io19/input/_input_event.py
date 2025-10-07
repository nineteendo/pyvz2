"""19.io class & function for dealing with Event input."""
# Standard libraries
from abc import ABCMeta, abstractmethod
from os import get_terminal_size
from typing import Any, Generic, Optional

# Custom libraries
from ..output.ansi import (cursor_horizontal_absolute, cursor_up,
                           erase_in_display)
from ..output.colors import bold, green
from ._classes import VALUE, CursorPosition, Representation
from .keyboard import CtrlCodes, Event, RawInput, read_event

__all__: list[str] = ['BaseInputEvent', 'InputEvent']
__all__ += ['input_event']


class BaseInputEvent(Generic[VALUE], metaclass=ABCMeta):
    """Base Input Event."""

    def __init__(
        self, title: Any, *, clear: bool = False,
        representation: type[str] = Representation
    ) -> None:
        """Make new BaseInputEvent instance."""
        screen_height: int
        screen_width: int
        screen_width, screen_height = get_terminal_size()
        self.clear: bool = clear
        self.cursor_position: CursorPosition = CursorPosition(screen_width)
        self.representation: type[str] = representation
        self.screen_height: int = screen_height
        self.screen_width: int = screen_width
        self.title: str = representation(title)

    def get_title(self) -> str:
        """Get title."""
        return self.title

    def move_back(self, cursor_back: int) -> None:
        """Move cursor back."""
        row: int = self.cursor_position.row
        self.cursor_position.move_back(cursor_back)
        cursor_up(row - self.cursor_position.row)
        cursor_horizontal_absolute(self.cursor_position.col)

    @abstractmethod
    def get_value(self) -> Optional[VALUE]:
        """Get value."""


class InputEvent(BaseInputEvent[Event]):
    """Input Event."""

    def get_value(self) -> Optional[Event]:
        """Get value."""
        RawInput.enable()
        self.screen_width, self.screen_height = get_terminal_size()
        title: str = self.get_title().replace('\n', ' ')
        self.cursor_position += 3 + len(title)
        print(green('?'), bold(title), end=' ', flush=True)
        read_event()
        event: Event = Event.queue.get_nowait()
        while not event.pressed:
            read_event()
            event = Event.queue.get_nowait()

        RawInput.disable()
        if not self.clear:
            print()
        else:
            self.move_back(self.cursor_position.chars)
            erase_in_display()

        return None if event.special == CtrlCodes.ESCAPE else event


def input_event(
    title: Any, *, clear: bool = False,
    representation: type[str] = Representation
) -> Optional[Event]:
    """Read Event from console input."""
    return InputEvent(
        title, clear=clear, representation=representation
    ).get_value()
