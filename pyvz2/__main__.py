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

import sys
from contextlib import suppress
from gettext import gettext as _

from clinteract import input_str
from rgbeep import ColoredOutput, NoCursor
from skiboard import RawInput


# Enable raw input, colored output & no cursor for entire program
@RawInput()
@ColoredOutput()
@NoCursor()
def main() -> None:
    """Start PyVZ2."""
    with suppress(EOFError, KeyboardInterrupt):
        input_str(_("Enter name:"), min_length=3)


# pylint: disable=consider-using-in
if sys.platform == "darwin" or sys.platform == "linux":  # noqa: PLR1714
    # pylint: disable=no-name-in-module
    from signal import SIG_DFL, SIGCONT, SIGTSTP, raise_signal, signal
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from types import FrameType

    def resume(_1: int, _2: FrameType | None) -> None:
        """Enable raw input & no cursor on resume."""
        signal(SIGTSTP, suspend)
        if NoCursor.count:
            NoCursor.enable()

        if RawInput.count:
            RawInput.enable()

    signal(SIGCONT, resume)

    def suspend(_1: int, _2: FrameType | None) -> None:
        """Disable raw input & no cursor on suspend."""
        NoCursor.disable()
        RawInput.disable()
        signal(SIGTSTP, SIG_DFL)
        raise_signal(SIGTSTP)

    signal(SIGTSTP, suspend)

if __name__ == "__main__":
    main()
