#!/usr/bin/env python
# python ~/OneDrive/Personal/GitHub/pyvz2
"""PyVZ2, a console utility to modify PVZ2."""
# TODO: Interactive menus
# TODO: Console arguments
# TODO: Translations
# TODO: Reimplement old functionality

__all__: list[str] = []

# Standard libraries
from gettext import gettext as _

# Custom libraries
from lib.colorized import ColoredOutput, NoCursor
from lib.io19.input import input_str
from lib.skiboard import RawInput


@RawInput()  # Enable raw input for entire program
@ColoredOutput()  # Enable colored output for entire program
@NoCursor()  # Enable no cursor for entire program
def main() -> None:
    """Start PyVZ2."""
    try:
        input_str(_('Enter name:'), min_length=3)
    except (EOFError, KeyboardInterrupt):
        pass  # Hide EOFError & KeyboardInterrupt


if __name__ == '__main__':
    main()
