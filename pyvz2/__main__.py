"""Python VS. Zombies 2 (PyVZ2)."""
from __future__ import annotations

__all__: list[str] = []
__version__: str = "2.0.0-dev"

from contextlib import suppress
from logging import FileHandler, Formatter, Logger, getLogger
from sys import stderr
from typing import TYPE_CHECKING, Any

import jsonyx
import jsonyx.allow
from utils import ErrorCounter, get_main_dir, path_input, process_items

if TYPE_CHECKING:
    from pathlib import Path

_logger: Logger = getLogger(__name__)


# pylint: disable-next=R0903
class _Config:
    def __init__(self, settings: dict[str, Any]) -> None:
        if settings.get("strict", True):
            allow: frozenset[str] = jsonyx.allow.NOTHING
        else:
            allow = jsonyx.allow.EVERYTHING

        item_separator: str = settings.get("item_separator", ", ")
        key_separator: str = settings.get("key_separator", ": ")
        self.json_decoder: jsonyx.Decoder = jsonyx.Decoder(allow=allow)
        self.json_encoder: jsonyx.Encoder = jsonyx.Encoder(
            allow=allow,
            end=settings.get("end", "\n"),
            ensure_ascii=settings.get("ensure_ascii", False),
            indent=settings.get("indent", 4),
            indent_leaves=settings.get("indent_leaves", True),
            max_indent_level=settings.get("max_indent_level", None),
            separators=(item_separator, key_separator),
            sort_keys=settings.get("sort_keys", False),
        )
        self.json_manipulator: jsonyx.Manipulator = jsonyx.Manipulator(
            allow=allow,
        )


def _json_diff(
    config: _Config, input_path: Path, input2_path: Path, output_path: Path,
) -> None:
    if input_path in output_path.parents:
        msg: str = "Output path cannot be a subdirectory of the input path"
        raise ValueError(msg)

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

    def callback(
        input_filename: Path, input2_filename: Path, output_filename: Path,
    ) -> None:
        try:
            obj: Any = config.json_decoder.read(input_filename)
            obj2: Any = config.json_decoder.read(input2_filename)
            if patch := jsonyx.make_patch(obj, obj2):
                config.json_encoder.write(patch, output_filename)
        except (
            jsonyx.TruncatedSyntaxError, OSError, RecursionError, TypeError,
            ValueError,
        ) as exc:
            exc.with_traceback(None)
            _logger.exception("Failed to generate JSON patch")

    if input_path.is_dir():
        output_dir: Path = output_path
    else:
        output_dir = output_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)
    process_items(
        collect_items(input_path, input2_path, output_path), callback,
    )


def _json_format(config: _Config, input_path: Path, output_path: Path) -> None:
    if input_path in output_path.parents:
        msg: str = "Output path cannot be a subdirectory of the input path"
        raise ValueError(msg)

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

    def callback(input_filename: Path, output_filename: Path) -> None:
        try:
            obj: Any = config.json_decoder.read(input_filename)
            config.json_encoder.write(obj, output_filename)
        except (
            jsonyx.TruncatedSyntaxError, OSError, RecursionError, TypeError,
            ValueError,
        ) as exc:
            exc.with_traceback(None)
            _logger.exception("Failed to format JSON file")

    if input_path.is_dir():
        output_dir: Path = output_path
    else:
        output_dir = output_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)
    process_items(collect_items(input_path, output_path), callback)


def _json_patch(
    config: _Config, input_path: Path, patch_path: Path, output_path: Path,
) -> None:
    if input_path in output_path.parents:
        msg: str = "Output path cannot be a subdirectory of the input path"
        raise ValueError(msg)

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

    def callback(
        input_filename: Path, patch_filename: Path, output_filename: Path,
    ) -> None:
        try:
            obj: Any = config.json_decoder.read(input_filename)
            patch: Any = config.json_decoder.read(patch_filename)
            obj = config.json_manipulator.apply_patch(obj, patch)
            config.json_encoder.write(obj, output_filename)
        except (
            AssertionError, jsonyx.TruncatedSyntaxError, LookupError, OSError,
            RecursionError, TypeError, ValueError,
        ) as exc:
            exc.with_traceback(None)
            _logger.exception("Failed to apply JSON patch")

    if input_path.is_dir():
        output_dir: Path = output_path
    else:
        output_dir = output_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)
    process_items(
        collect_items(input_path, patch_path, output_path), callback,
    )


def _interactive_main() -> None:
    settings: dict[str, Any] = jsonyx.read(
        get_main_dir() / "settings.jsonc",
        allow=jsonyx.allow.COMMENTS | jsonyx.allow.TRAILING_COMMA,
    )
    config: _Config = _Config(settings)
    print(f"Python VS. Zombies 2 v{__version__}")
    print()
    print("Tools:")
    print("a: JSON diff")
    print("b: JSON format")
    print("c: JSON patch")
    if (tool := input("Choose tool: ")) == "a":
        input_path: Path = path_input("First JSON input file or directory: ")
        if input_path.is_dir():
            input2_path: Path = path_input("Second JSON input directory: ")
            output_path: Path = path_input("JSON output directory: ")
        else:
            input2_path = path_input("Second JSON input file")
            output_path = path_input("JSON output file: ")

        _json_diff(config, input_path, input2_path, output_path)
    elif tool == "b":
        input_path = path_input("JSON input file or directory: ")
        if input_path.is_dir():
            output_path = path_input("JSON output directory: ")
        else:
            output_path = path_input("JSON output file: ")

        _json_format(config, input_path, output_path)
    elif tool == "c":
        input_path = path_input("JSON input file or directory: ")
        if input_path.is_dir():
            patch_path: Path = path_input("JSON patch directory: ")
            output_path = path_input("JSON output directory: ")
        else:
            patch_path = path_input("JSON patch file")
            output_path = path_input("JSON output file: ")

        _json_patch(config, input_path, patch_path, output_path)
    else:
        stderr.write(f"Invalid tool: {tool!r}\n")


def _main() -> None:
    log_file: Path = get_main_dir() / "pyvz2.log"
    handler: FileHandler = FileHandler(log_file, "w", "utf-8")
    fmt: str = "%(asctime)s - %(levelname)s - %(message)s"
    handler.setFormatter(Formatter(fmt))
    _logger.addHandler(handler)
    error_counter: ErrorCounter = ErrorCounter()
    _logger.addFilter(error_counter)
    try:
        _interactive_main()
    # pylint: disable-next=W0718
    except Exception:
        _logger.exception("Something went wrong")

    if error_counter.count:
        stderr.write(f"Something went wrong, check: {log_file}\n")

    input("Press enter to continue...")


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        _main()
