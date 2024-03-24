"""CLInteract typevar, classes & functions for custom command line input."""
# Copyright (C) 2023-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = [
    "VALUE",
    "BaseInputHandler",
    "BaseTextInput",
    "ContextEvent",
    "Cursor",
    "InputStr",
    "Pause",
    "Representation",
    "get_allowed",
    "get_contexts",
    "get_shortcuts",
    "iscategory",
]
__author__: str = "Nice Zombies"

from ._custom import (
    VALUE, ContextEvent, Cursor, Representation, get_allowed, get_contexts,
    get_shortcuts, iscategory,
)
from ._input_str import BaseTextInput, InputStr
from ._pause import BaseInputHandler, Pause
