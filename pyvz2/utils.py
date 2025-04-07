"""Python VS. Zombies 2 (PyVZ2)."""
# TODO(Nice Zombies): add tests
from __future__ import annotations

__all__: list[str] = ["parse_path", "process_items"]

from pathlib import Path
from shutil import get_terminal_size
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

    _T = TypeVar("_T")


def parse_path(string: str) -> Path:
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
        else:
            trailing_spaces += " "

    if escaped:
        new_string += "\\"

    return Path(new_string)


def process_items(items: list[_T], callback: Callable[[_T], None]) -> None:
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
        callback(item)
        if progress := full[width * (i - 1) // total:width * i // total]:
            print(end=progress, flush=True)

    print("]")
