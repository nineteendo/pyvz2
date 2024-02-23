"""CLInteract typevar & classes for command line input."""
# Copyright (C) 2023-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "VALUE",
    "BaseInputHandler",
    "BaseTextInput",
    "Cursor",
    "InputStr",
    "Pause",
    "Representation",
]
__author__: str = "Nice Zombies"

from ._classes import VALUE, Cursor, Representation
from ._input_str import BaseTextInput, InputStr
from ._pause import BaseInputHandler, Pause
