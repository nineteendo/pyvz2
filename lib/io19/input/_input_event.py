"""19.io class & function for event input."""
# Standard libraries
from abc import ABCMeta, abstractmethod
from math import prod
from os import get_terminal_size
from typing import Generic

# Custom libraries
from ...colorized import (ColoredOutput, NoCursor, RestoreCursor, bold,
                          erase_in_display, green, invert)
from ...skiboard import Event, RawInput, get_event
from ._classes import VALUE, Representation

__all__: list[str] = ['BaseInputEvent', 'InputEvent']
__all__ += ['input_event']


class BaseInputEvent(Generic[VALUE], metaclass=ABCMeta):
    """Base class for input events."""

    def __init__(
        self, prompt: object, *, representation: type[str] = Representation
    ) -> None:
        self.representation: type[str] = representation
        self.prompt:         str = representation(prompt)

    @RestoreCursor()
    def display(self) -> None:
        """Display information."""
        prompt: str = self.get_prompt()
        length: int = len(' '.join(('?', prompt, ' ')))
        offset: int = max(length - prod(get_terminal_size()), 0)
        print(
            green('?'), bold(prompt[offset:]), invert(' '), end='', flush=True
        )

    def get_prompt(self) -> str:
        """Get prompt for user."""
        return self.prompt

    @abstractmethod
    def get_value(self) -> VALUE:
        """Get value from user."""


class InputEvent(BaseInputEvent[Event]):
    """Class for input events."""

    @RawInput()
    @ColoredOutput()
    @NoCursor()
    def get_value(self) -> Event:
        self.display()
        event: Event = get_event()
        while not event.ispressed():
            event = get_event()

        erase_in_display()
        return event


def input_event(
    prompt: object, *, representation: type[str] = Representation
) -> Event:
    """Read event from console input."""
    return InputEvent(prompt, representation=representation).get_value()
