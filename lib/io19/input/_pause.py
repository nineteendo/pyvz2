"""19.io class & function for pausing."""
# Standard libraries
from abc import ABCMeta, abstractmethod
from gettext import gettext as _
from math import prod
from os import get_terminal_size
from typing import Generic

# Custom libraries
from ...colorized import (ColoredOutput, NoCursor, RestoreCursor, bold,
                          erase_in_display, green, invert)
from ...skiboard import Event, RawInput, get_event
from ._classes import VALUE, Representation

__all__: list[str] = ['BaseInputHandler', 'Pause']
__all__ += ['pause']


class BaseInputHandler(Generic[VALUE], metaclass=ABCMeta):
    """Base class for handling console input."""

    def __init__(
        self, prompt: object = _('Press any key...'), *,
        representation: type[str] = Representation
    ) -> None:
        self.prompt:         str = representation(prompt)
        self.representation: type[str] = representation

    @RestoreCursor()
    def display(self) -> None:
        """Display information."""
        print(end='\r')
        prompt: str = self.get_prompt()
        length: int = len(' '.join(('?', prompt, '')))
        offset: int = max(length - prod(get_terminal_size()), 0)
        print(green('?'), bold(prompt[offset:]), end=invert(' '), flush=True)
        erase_in_display()

    def get_prompt(self) -> str:
        """Get prompt for user."""
        return self.prompt

    @abstractmethod
    def get_value(self) -> VALUE:
        """Get value from user."""


class Pause(BaseInputHandler[None]):
    """Class for pausing."""

    @RawInput()
    @ColoredOutput()
    @NoCursor()
    def get_value(self) -> None:
        self.display()
        event: Event = get_event()
        while not event.ispressed():
            event = get_event()

        erase_in_display()


def pause(
    prompt: object = _('Press any key...'), *,
    representation: type[str] = Representation
) -> None:
    """Pause with message."""
    Pause(prompt, representation=representation).get_value()
