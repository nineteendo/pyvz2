"""19.io class & function for event input."""
# Standard libraries
from abc import ABCMeta, abstractmethod
from typing import Generic

# Custom libraries
from ._classes import VALUE, Representation
from .keyboard import Event, RawInput, get_event

__all__: list[str] = ['VALUE']
__all__ += ['BaseInputEvent', 'InputEvent']
__all__ += ['input_event']


class BaseInputEvent(Generic[VALUE], metaclass=ABCMeta):
    """Base class for input events."""

    def __init__(
        self, title: object, *, representation: type[str] = Representation
    ) -> None:
        self.representation: type[str] = representation
        self.title:          str = representation(title)

    def display(self) -> None:
        print(end=self.get_title(), flush=True)

    def get_title(self) -> str:  # pylint: disable=missing-function-docstring
        return self.title

    @RawInput()
    @abstractmethod
    def get_value(self) -> VALUE:  # pylint: disable=missing-function-docstring
        pass


class InputEvent(BaseInputEvent[Event]):
    """Class for input events."""

    @RawInput()
    def get_value(self) -> Event:
        self.display()
        event: Event = get_event()
        while not event.ispressed():
            event = get_event()

        print()
        return event


def input_event(
    title: object, *, representation: type[str] = Representation
) -> Event:
    """Read event from console input."""
    return InputEvent(title, representation=representation).get_value()
