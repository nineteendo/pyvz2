#!/usr/bin/env python
"""PyVZ2, a command line utility to modify PVZ2."""
# Copyright (C) 2020-2024 Nice Zombies
# TODO(Nice Zombies): Error logging
# TODO(Nice Zombies): Interactive menus
# TODO(Nice Zombies): CLInteract demo
# TODO(Nice Zombies): Translations
# TODO(Nice Zombies): Custom keyboard shortcuts
# TODO(Nice Zombies): Update checking
# TODO(Nice Zombies): Reimplement old functionality
# TODO(Nice Zombies): Command line arguments
from __future__ import annotations

from argparse import ArgumentParser, Namespace

__all__: list[str] = []
__author__: str = "Nice Zombies"
__version__: str = "2.0"

from contextlib import suppress
from gettext import gettext as _

from clinteract import input_str
from clinteract.custom import get_shortcuts
from contextile import (
    application_keypad, colored_output, mouse_input, no_cursor, raw_input,
)
from skiboard import get_input_event


class PyVZ2Namespace(Namespace):  # pylint: disable=too-few-public-methods
    """Namespace of PyVZ2."""

    func: str | None


# Enable raw & mouse input, application_keypad, colored output and no cursor
# for entire program
@raw_input
@application_keypad
@mouse_input
@colored_output
@no_cursor
def main() -> None:
    """Start PyVZ2."""
    parser: ArgumentParser = ArgumentParser(
        description="PyVZ2, a command line utility to modify PVZ2",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s v{__version__}",
    )
    parser.add_argument("func", nargs="?", choices={"keyboard"})
    args: PyVZ2Namespace = parser.parse_args(namespace=PyVZ2Namespace())
    with suppress(EOFError, KeyboardInterrupt):
        if args.func is None:
            shortcuts: dict[str, list[str]] = get_shortcuts()
            shortcuts["Move cursor back"] = []
            shortcuts["Move cursor forward"] = []
            shortcuts["Scroll cursor back"] = ["ctrl+b", "left"]
            shortcuts["Scroll cursor forward"] = ["ctrl+f", "right"]
            input_str(_("Enter a string:"), shortcuts=shortcuts)
        else:
            while True:
                print(repr(get_input_event().shortcut))


if __name__ == "__main__":
    main()
