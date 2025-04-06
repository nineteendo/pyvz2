"""Python VS. Zombies 2 (PyVZ2)."""
from __future__ import annotations

__all__: list[str] = []
__version__: str = "2.0.0-dev"

from contextlib import suppress
from pathlib import Path
from shutil import get_terminal_size
from typing import TYPE_CHECKING, Any, TypeVar

import jsonyx

if TYPE_CHECKING:
    from collections.abc import Callable

    _T = TypeVar("_T")

_decoder: jsonyx.Decoder = jsonyx.Decoder()
_encoder: jsonyx.Encoder = jsonyx.Encoder(indent=4)


def _process_items(items: list[_T], callback: Callable[[_T], None]) -> None:
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


def _format_json() -> None:
    input_path: Path = Path(input("JSON input file or directory: "))
    if input_path.is_dir():
        output_path: Path = Path(input("JSON output directory: "))
        output_dir: Path = output_path
    else:
        output_path = Path(input("JSON output file: "))
        output_dir = output_path.parent

    def collect_files(
        input_path: Path, output_path: Path,
    ) -> list[tuple[Path, Path]]:
        if not input_path.is_dir():  # crash if the path doesn't exist
            return [(input_path, output_path)]

        files: list[tuple[Path, Path]] = []
        output_path.mkdir(exist_ok=True)
        for item in sorted(input_path.iterdir()):
            if not item.name.startswith(".") and (
                item.is_dir() or item.suffix.lower() == ".json"
            ):
                files.extend(collect_files(item, output_path / item.name))

        return files

    def format_json_file(item: tuple[Path, Path]) -> None:
        input_filename, output_filename = item
        obj: Any = _decoder.read(input_filename)
        _encoder.write(obj, output_filename)

    output_dir.mkdir(parents=True, exist_ok=True)
    files: list[tuple[Path, Path]] = collect_files(input_path, output_dir)
    _process_items(files, format_json_file)


def _interactive_main() -> None:
    print(f"Python VS. Zombies 2 v{__version__}")
    print()
    print("Format JSON")
    _format_json()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        _interactive_main()
