"""19.io classes for console input."""
# pylint: disable=unused-import
# Custom libraries
from ._classes import VALUE, Representation
from ._input_event import BaseInputEvent, InputEvent

__all__: list[str] = ['VALUE']
__all__ += ['BaseInputEvent', 'InputEvent', 'Representation']
