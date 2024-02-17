#!/usr/bin/env python
"""PyVZ2, a command line utility to modify PVZ2."""
# Copyright (C) 2020-2024 Nice Zombies
# TODO(Nice Zombies): Interactive menus
# TODO(Nice Zombies): Command line arguments
# TODO(Nice Zombies): Translations
# TODO(Nice Zombies): Reimplement old functionality
from __future__ import annotations

__all__: list[str] = []
__author__: str = "Nice Zombies"
__version__: str = "2.0"

from contextlib import suppress

from contextile import (
    application_keypad, colored_output, mouse_input, no_cursor, raw_input,
)
from skiboard import get_event


# Enable raw & mouse input, colored output and no cursor for entire program
@raw_input
@application_keypad
@mouse_input
@colored_output
@no_cursor
def main() -> None:
    """Start PyVZ2."""
    with suppress(EOFError, KeyboardInterrupt):
        while True:
            print(repr(get_event()))


if __name__ == "__main__":
    main()
