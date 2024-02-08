"""19.io typevar & classes for console input."""
__all__: list[str] = [
    # SCREAMING_SNAKE_CASE
    'VALUE',
    # PascalCase
    'BaseInputHandler', 'BaseInputStr', 'ContextEvent', 'Cursor', 'InputStr',
    'Pause', 'Representation'
]

# pylint: disable=unused-import
# Custom libraries
from ._classes import VALUE, ContextEvent, Cursor, Representation
from ._input_str import BaseInputStr, InputStr
from ._pause import BaseInputHandler, Pause
