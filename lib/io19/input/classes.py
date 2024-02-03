"""19.io classes for console input."""
# pylint: disable=unused-import
# Custom libraries
from ._classes import VALUE, Representation
from ._pause import BaseInputHandler, Pause

__all__: list[str] = ['VALUE']
__all__ += ['BaseInputHandler', 'Pause', 'Representation']
