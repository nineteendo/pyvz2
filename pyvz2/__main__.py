"""Python VS. Zombies 2 (PyVZ2)."""
# TODO(Nice Zombies): add error handling
from __future__ import annotations

__all__: list[str] = []
__version__: str = "2.0.0-dev"

from contextlib import suppress
from typing import TYPE_CHECKING, Any

import jsonyx
from utils import parse_path, process_items

if TYPE_CHECKING:
    from pathlib import Path

# TODO(Nice Zombies): load configuration from settings
_decoder: jsonyx.Decoder = jsonyx.Decoder()
_encoder: jsonyx.Encoder = jsonyx.Encoder(indent=4)
_manipulator: jsonyx.Manipulator = jsonyx.Manipulator()


def _json_diff(input_path: Path, input2_path: Path, output_path: Path) -> None:
    def collect_items(
        input_path: Path, input2_path: Path, output_path: Path,
    ) -> list[tuple[Path, Path, Path]]:
        if not input_path.is_dir():  # crash if the path doesn't exist
            return [(input_path, input2_path, output_path)]

        items: list[tuple[Path, Path, Path]] = []
        output_path.mkdir(exist_ok=True)
        for new_input_path in sorted(input_path.iterdir()):
            new_input2_path: Path = input2_path / new_input_path.name
            new_output_path: Path = output_path / new_input_path.name
            if new_input_path.is_dir():
                pass
            elif new_input_path.suffix.lower() == ".json":
                new_output_path = new_output_path.with_suffix(".patch.json")
            else:
                continue

            if (
                new_input_path.name.startswith(".")
                or not new_input2_path.exists()
            ):
                continue

            items.extend(collect_items(
                new_input_path, new_input2_path, new_output_path,
            ))

        return items

    def callback(item: tuple[Path, Path, Path]) -> None:
        input_filename, input2_filename, output_filename = item
        obj: Any = _decoder.read(input_filename)
        obj2: Any = _decoder.read(input2_filename)
        if patch := jsonyx.make_patch(obj, obj2):
            _encoder.write(patch, output_filename)
        else:
            output_filename.unlink(missing_ok=True)

    if input_path.is_dir():
        output_dir: Path = output_path
    else:
        output_dir = output_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)
    process_items(
        collect_items(input_path, input2_path, output_path), callback,
    )


def _json_format(input_path: Path, output_path: Path) -> None:
    def collect_items(
        input_path: Path, output_path: Path,
    ) -> list[tuple[Path, Path]]:
        if not input_path.is_dir():  # crash if the path doesn't exist
            return [(input_path, output_path)]

        items: list[tuple[Path, Path]] = []
        output_path.mkdir(exist_ok=True)
        for new_input_path in sorted(input_path.iterdir()):
            new_output_path: Path = output_path / new_input_path.name
            if not new_input_path.name.startswith(".") and (
                new_input_path.is_dir()
                or new_input_path.suffix.lower() == ".json"
            ):
                items.extend(collect_items(new_input_path, new_output_path))

        return items

    def callback(item: tuple[Path, Path]) -> None:
        input_filename, output_filename = item
        obj: Any = _decoder.read(input_filename)
        _encoder.write(obj, output_filename)

    if input_path.is_dir():
        output_dir: Path = output_path
    else:
        output_dir = output_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)
    process_items(collect_items(input_path, output_path), callback)


def _json_patch(input_path: Path, patch_path: Path, output_path: Path) -> None:
    def collect_items(
        input_path: Path, patch_path: Path, output_path: Path,
    ) -> list[tuple[Path, Path, Path]]:
        if not input_path.is_dir():  # crash if the path doesn't exist
            return [(input_path, patch_path, output_path)]

        items: list[tuple[Path, Path, Path]] = []
        output_path.mkdir(exist_ok=True)
        for new_input_path in sorted(input_path.iterdir()):
            new_patch_path: Path = patch_path / new_input_path.name
            new_output_path: Path = output_path / new_input_path.name
            if new_input_path.is_dir():
                pass
            elif new_input_path.suffix.lower() == ".json":
                new_patch_path = new_patch_path.with_suffix(".patch.json")
            else:
                continue

            if (
                new_input_path.name.startswith(".")
                or not new_patch_path.exists()
            ):
                continue

            items.extend(collect_items(
                new_input_path, new_patch_path, new_output_path,
            ))

        return items

    def callback(item: tuple[Path, Path, Path]) -> None:
        input_filename, patch_filename, output_filename = item
        obj: Any = _decoder.read(input_filename)
        patch: Any = _decoder.read(patch_filename)
        obj = _manipulator.apply_patch(obj, patch)
        _encoder.write(obj, output_filename)

    if input_path.is_dir():
        output_dir: Path = output_path
    else:
        output_dir = output_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)
    process_items(
        collect_items(input_path, patch_path, output_path), callback,
    )


def _interactive_main() -> None:
    print(f"Python VS. Zombies 2 v{__version__}")
    print()
    print("Tools:")
    print("a: JSON diff")
    print("b: JSON format")
    print("c: JSON patch")
    tool: str = input("Choose tool: ")
    if tool == "a":
        input_path: Path = parse_path(
            input("First JSON input file or directory: "),
        )
        if input_path.is_dir():
            input2_path: Path = parse_path(
                input("Second JSON input directory: "),
            )
            output_path: Path = parse_path(input("JSON output directory: "))
        else:
            input2_path = parse_path(input("Second JSON input file"))
            output_path = parse_path(input("JSON output file: "))

        _json_diff(input_path, input2_path, output_path)
    elif tool == "b":
        input_path = parse_path(input("JSON input file or directory: "))
        if input_path.is_dir():
            output_path = parse_path(input("JSON output directory: "))
        else:
            output_path = parse_path(input("JSON output file: "))

        _json_format(input_path, output_path)
    elif tool == "c":
        input_path = parse_path(input("JSON input file or directory: "))
        if input_path.is_dir():
            patch_path: Path = parse_path(input("JSON patch directory: "))
            output_path = parse_path(input("JSON output directory: "))
        else:
            patch_path = parse_path(input("JSON patch file"))
            output_path = parse_path(input("JSON output file: "))

        _json_patch(input_path, patch_path, output_path)
    else:
        msg: str = "Unknown tool"
        raise ValueError(msg)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        _interactive_main()
