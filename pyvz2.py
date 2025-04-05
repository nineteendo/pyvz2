"""Python VS. Zombies 2 (PyVZ2)."""
from __future__ import annotations

__all__: list[str] = []
__version__: str = "2.0.0-dev"

from contextlib import suppress
from pathlib import Path
from shutil import get_terminal_size
from time import time
from typing import TYPE_CHECKING, Any, TypeVar

import jsonyx

if TYPE_CHECKING:
    from collections.abc import Callable

    _T = TypeVar("_T")

_RED: str = "\033[91m"
_GREEN: str = "\033[92m"
_YELLOW: str = "\033[93m"
_RESET: str = "\033[0m"

_decoder: jsonyx.Decoder = jsonyx.Decoder()
_encoder: jsonyx.Encoder = jsonyx.Encoder(indent=4)


def _process_items(
    items: list[tuple[str, _T]],
    callback: Callable[[_T], None],
    *,
    colored: bool = False,
    verbose: bool = False,
) -> None:
    failed: int = 0
    succeeded: int = 0
    width: int = get_terminal_size().columns
    print(f" Processing {len(items)} items ".center(width, "="))
    start_time: float = time()
    for i, (name, item) in enumerate(items, start=1):
        try:
            callback(item)
            status: str = "SUCCEEDED"
            succeeded += 1
        # pylint: disable=W0718
        except Exception:  # noqa: BLE001
            status = "FAILED"
            failed += 1

        percentage: str = f"[{100 * i // len(items):3d}%]"
        if not colored:
            display_percentage: str = percentage
        elif failed:
            display_percentage = f"{_RED}{percentage}{_RESET}"
        else:
            display_percentage = f"{_GREEN}{percentage}{_RESET}"

        if verbose:
            length: int = len(f"{status} {name} {percentage}")
            padding: str = " " * (width - length % width)
            if not colored:
                display_status: str = status
            elif status == "SUCCEEDED":
                display_status = f"{_GREEN}{status}{_RESET}"
            else:
                display_status = f"{_RED}{status}{_RESET}"

            print(f"{display_status} {name}{padding} {display_percentage}")
            continue

        if status == "SUCCEEDED":
            dot: str = "."
            if colored:
                dot = f"{_GREEN}{dot}{_RESET}"
        else:
            dot = "F"
            if colored:
                dot = f"{_RED}{dot}{_RESET}"

        print(end=dot, flush=True)
        if not i % (width - 7) or i == len(items):
            # count written dots
            dots: str = "?" * ((i - 1) % (width - 7) + 1)
            length = len(f"{dots} {percentage}")
            padding = " " * (width - length)
            print(f"{padding} {display_percentage}")

    elapsed_time: float = time() - start_time
    msg: str = ""
    display_msg: str = ""
    if failed:
        msg = f"{failed} failed"
        display_msg = msg
        if colored:
            display_msg = f"{_RED}{msg}{_RESET}"

    if succeeded:
        new_msg: str = f"{succeeded} succeeded"
        new_display_msg: str = new_msg
        if colored:
            new_display_msg = f"{_GREEN}{new_display_msg}{_RESET}"

        if msg:
            msg += f", {new_msg}"
            display_msg += f", {new_display_msg}"
        else:
            msg = new_msg
            display_msg = new_display_msg

    if not items:
        msg = "no items processed"
        display_msg = msg
        if colored:
            display_msg = f"{_YELLOW}{display_msg}{_RESET}"

    length = len(f" {msg} in {elapsed_time:.2f}s ")
    left_padding: str = "=" * ((width - length) // 2)
    right_padding: str = "=" * ((width - length + 1) // 2)
    print(
        f"{left_padding} {display_msg} in {elapsed_time:.2f}s {right_padding}",
    )


def _format_json() -> None:
    input_path: Path = Path(input("JSON input file or directory: "))
    if input_path.is_dir():
        output_path: Path = Path(input("JSON output directory: "))
        output_dir: Path = output_path
    else:
        output_path = Path(input("JSON output file: "))
        output_dir = output_path.parent

    def collect_files(
        name: Path, input_path: Path, output_path: Path,
    ) -> list[tuple[str, tuple[Path, Path]]]:
        if not input_path.is_dir():  # crash if the path doesn't exist
            return [(str(name), (input_path, output_path))]

        files: list[tuple[str, tuple[Path, Path]]] = []
        output_path.mkdir(exist_ok=True)
        for item in sorted(input_path.iterdir()):
            if not item.name.startswith(".") and (
                item.is_dir() or item.suffix.lower() == ".json"
            ):
                files.extend(collect_files(
                    name / item.name, item, output_path / item.name,
                ))

        return files

    def format_json_file(item: tuple[Path, Path]) -> None:
        input_filename, output_filename = item
        obj: Any = _decoder.read(input_filename)
        _encoder.write(obj, output_filename)

    output_dir.mkdir(parents=True, exist_ok=True)
    files: list[tuple[str, tuple[Path, Path]]] = collect_files(
        Path(), input_path, output_dir,
    )
    _process_items(files, format_json_file, colored=True)


def _interactive_main() -> None:
    print(f"Python VS. Zombies 2 v{__version__}")
    print()
    print("Format JSON")
    _format_json()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        _interactive_main()
