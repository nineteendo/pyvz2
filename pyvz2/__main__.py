"""Python VS. Zombies 2 (PyVZ2)."""
from __future__ import annotations

__all__: list[str] = []
__version__: str = "2.0.0-dev"

from contextlib import suppress
from typing import TYPE_CHECKING, Any

import jsonyx
from utils import parse_path, process_items

if TYPE_CHECKING:

    from pathlib import Path

_decoder: jsonyx.Decoder = jsonyx.Decoder()
_encoder: jsonyx.Encoder = jsonyx.Encoder(indent=4)


def _format_json() -> None:
    input_path: Path = parse_path(input("JSON input file or directory: "))
    if input_path.is_dir():
        output_path: Path = parse_path(input("JSON output directory: "))
        output_dir: Path = output_path
    else:
        output_path = parse_path(input("JSON output file: "))
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
    process_items(files, format_json_file)


def _interactive_main() -> None:
    print(f"Python VS. Zombies 2 v{__version__}")
    print()
    print("Format JSON")
    _format_json()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        _interactive_main()
