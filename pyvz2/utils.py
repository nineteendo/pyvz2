"""pyvz2 utility functions."""
from __future__ import annotations

__all__: list[str] = [
    "ErrorCounter",
    "get_main_dir",
    "parse_path",
    "path_input",
    "process_items",
]

import sys
from logging import ERROR, Filter, LogRecord
from pathlib import Path
from shutil import get_terminal_size
from sys import executable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


# pylint: disable-next=R0903
class ErrorCounter(Filter):
    """Error counter."""

    def __init__(self) -> None:
        """Create new error counter."""
        super().__init__()
        self.count: int = 0

    def filter(self, record: LogRecord) -> bool:
        """Update error count."""
        if record.levelno >= ERROR:
            self.count += 1

        return True


def get_main_dir() -> Path:
    """Get the directory of the main script."""
    if getattr(sys, "frozen", False):
        main_dir: str = executable
    else:
        main_dir = sys.path[0]

    return Path(main_dir).parent


if sys.platform == "win32":
    def parse_path(string: str) -> str:
        """Parse path."""
        end_quote: str | None = None
        new_string: str = ""
        trailing_spaces: str = ""
        for char in string:
            if char != " ":
                new_string += trailing_spaces
                trailing_spaces = ""

            if char == end_quote:
                end_quote = None
            elif char == '"' and not end_quote:
                end_quote = char
            elif char != " " or end_quote:
                new_string += char
            elif new_string:
                trailing_spaces += " "

        return new_string
else:
    def parse_path(string: str) -> str:
        """Parse path."""
        escaped: bool = False
        end_quote: str | None = None
        new_string: str = ""
        trailing_spaces: str = ""
        for char in string:
            if char != " ":
                new_string += trailing_spaces
                trailing_spaces = ""

            if escaped:
                escaped = False
                if char in {"\\", " ", "'", '"'}:
                    new_string += char
                else:
                    new_string += "\\" + char
            elif char == "\\":
                escaped = True
            elif char == end_quote:
                end_quote = None
            elif char in {'"', "'"} and not end_quote:
                end_quote = char
            elif char != " " or end_quote:
                new_string += char
            elif new_string:
                trailing_spaces += " "

        if escaped:
            new_string += "\\"

        return new_string


def path_input(prompt: str = "") -> Path:
    """Input path."""
    return Path(parse_path(input(prompt)))


def process_items(
    items: list[tuple[Any, ...]], callback: Callable[..., None],
) -> None:
    """Process items."""
    if not (total := len(items)):
        return

    width: int = max(20, get_terminal_size().columns) - 2
    full: str = "." * width
    for end in range(width, 0, -10):
        percentage: str = f"{100 * end // width}%"
        if (start := end - len(percentage)) >= 0:
            full = full[:start] + percentage + full[end:]

    print(end="[", flush=True)
    for i, item in enumerate(items, start=1):
        callback(*item)
        if progress := full[width * (i - 1) // total:width * i // total]:
            print(end=progress, flush=True)

    print("]")
