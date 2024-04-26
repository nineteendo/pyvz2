"""CLInteract class & function for str input."""
# Copyright (C) 2023-2024 Nice Zombies
# TODO(Nice Zombies): Alt + right click is disabled
# TODO(Nice Zombies): Selecting text is disabled
from __future__ import annotations

__all__: list[str] = ["BaseTextInput", "InputStr", "input_str"]
__author__: str = "Nice Zombies"

from contextlib import ExitStack
from gettext import gettext as _
from math import prod
from sys import stdin, stdout
from threading import Lock, Thread
from typing import Literal

from ansio import TerminalContext, colored_output, no_cursor, raw_input
from ansio.colors import cyan, grey, invert
from ansio.input import InputEvent, get_input_event

from ._custom import (
    ContextEvent, Cursor, Representation, get_allowed, get_shortcuts,
    iscategory,
)
from ._pause import BaseInputHandler
from .utils import beep, format_real, raw_print, set_cursor_position

_DELAY: float = 1 / 10
_ELLIPSIS: str = "\u2026"


# pylint: disable=too-many-instance-attributes
class BaseTextInput(BaseInputHandler[str]):
    """Base class for text input."""

    # pylint: disable=too-many-arguments, too-many-locals, too-many-statements
    def __init__(  # noqa: PLR0913, C901
        self,
        prompt: object = "",
        *,
        allowed: set[Literal[
            "letters", "marks", "numbers", "punctuations", "separators",
            "symbols",
        ]] | None = None,
        clear: bool = False,
        contexts: list[TerminalContext] | None = None,
        max_length: int | None = None,
        min_length: int = 0,
        placeholder: str | None = None,
        representation: type[str] = Representation,
        shortcuts: dict[str, list[str]] | None = None,
        transform_to: Literal["lowercase", "uppercase", None] = None,
        unicode: bool = True,
        value: str | None = None,
        whitelist: str = "",
    ) -> None:
        err: str
        if not allowed:
            # Allow everything when nothing is explicitly allowed
            allowed = set() if whitelist else get_allowed(unicode=unicode)

        if "marks" in allowed and not unicode:
            err = "there are no ascii marks"
            raise ValueError(err)

        if max_length is not None and max_length < 1:
            err = "max_length is smaller than 1"
            raise ValueError(err)

        if min_length < 0 or (
            max_length is not None and min_length > max_length
        ):
            err = "min_length doesn't lay between 0 & max_length"
            raise ValueError(err)

        if not shortcuts:
            shortcuts = get_shortcuts()

        invalid_char: str | None = next(
            (char for char in whitelist if not char.isprintable()), None,
        )
        if invalid_char:
            err = (
                "whitelist contains an unprintable character: "
                f"{invalid_char!r}"
            )
            raise ValueError(err)

        whitelist = whitelist.lower()
        if not value:
            value = ""
        elif max_length is not None and len(value) > max_length:
            err = "value is longer than max_length"
            raise ValueError(err)

        # Initialise variables for self.is_invalid_char
        self.allowed: set[Literal[
            "letters", "marks", "numbers", "punctuations", "separators",
            "symbols",
        ]] = allowed
        self.unicode: bool = unicode
        self.whitelist: str = whitelist
        invalid_char = next(
            (char for char in value if self.is_invalid_char(char)), None,
        )
        if invalid_char:
            err = f"value contains an invalid character: {invalid_char!r}"
            raise ValueError(err)

        if transform_to == "lowercase":
            value = value.lower()
        elif transform_to == "uppercase":
            value = value.upper()

        if placeholder is None:
            placeholder = _("Enter text...")

        self.clear: bool = clear
        self.max_length: int | None = max_length
        self.text_position: int = len(value)
        self.text_scroll: int = 0
        self.min_length: int = min_length
        self.placeholder: str = representation(placeholder)
        self.lock: Lock = Lock()
        self.ready_event: ContextEvent = ContextEvent()
        self.shortcuts: dict[str, list[str]] = shortcuts
        self.transform_to: Literal["lowercase", "uppercase", None]
        self.transform_to = transform_to
        self.value: str = value
        super().__init__(
            prompt,
            contexts=contexts,
            representation=representation,
        )

    def display_thread(self) -> None:
        """Display information on separate thread."""
        while True:
            with self.lock:
                if self.ready_event.is_set():
                    break

                msg: str = self.value or self.placeholder
                self.clear_screen()
                if self.enlarge_window():
                    self.print_error(_("Enlarge window"))
                else:
                    self.print_prompt(f" {msg} ")
                    self.print_msg(msg)
                    raw_print("\r\n")
                    self.cursor.moved_next_line()
                    err: str = self.invalid_value(self.value)
                    if err:
                        self.print_error(err)

                stdout.buffer.flush()

            if self.ready_event.wait(_DELAY):
                break

    def enlarge_window(self) -> bool:
        """Check if window is too small."""
        return self.terminal_size.lines < 2

    def get_value_offset(self, *, short: bool = False) -> int:
        """Get scroll offset for value."""
        max_chars: int = prod(self.terminal_size)
        if not short:
            max_chars -= self.terminal_size.columns

        prompt_len: int = len(f"? {self.get_prompt()}")
        msg: str = self.value or self.placeholder
        msg_len: int = len(f" {msg} ")
        return max(0, msg_len + min(prompt_len, max_chars // 2) - max_chars)

    @raw_input
    @colored_output
    @no_cursor
    def get_value(self) -> str | None:
        if not stdin.isatty() or not stdout.isatty():
            err: str = "stdin / stdout don't refer to a terminal"
            raise RuntimeError(err)

        with self.ready_event, ExitStack() as stack:
            for context in self.contexts:
                stack.enter_context(context)

            Thread(target=self.display_thread).start()
            while True:
                event: InputEvent = get_input_event()
                if event.moving or not event.pressed:
                    continue

                with self.lock:
                    if self.enlarge_window():
                        beep()
                        continue

                    if self.handle_input_event(event):
                        self.handle_scroll()
                        continue

                    if self.is_shortcut(event, "Cancel"):
                        self.clear_screen()
                        return None

                    if (
                        self.is_shortcut(event, "Submit input")
                        and not self.invalid_value(self.value)
                    ):
                        break

                    beep()

        if self.clear:
            self.clear_screen()
        else:
            msg: str = self.representation(self.value)
            self.clear_screen()
            self.print_prompt(f" {msg} ", short=True)
            self.print_msg(msg, short=True)
            raw_print("\r\n", flush=True)

        return self.value

    # pylint: disable=too-many-branches
    def handle_input_event(  # noqa: C901, PLR0912
        self,
        event: InputEvent,
    ) -> bool:
        """Handle input event."""
        start: str = self.value[:self.text_scroll + self.text_position]
        end: str = self.value[self.text_scroll + self.text_position:]
        if self.is_shortcut(event, "Clear screen"):
            set_cursor_position()
            self.cursor = Cursor(self.terminal_size.columns)
        elif self.is_shortcut(event, "Delete char after cursor") and end:
            self.value = start + end[1:]
        elif self.is_shortcut(event, "Delete char before cursor") and start:
            self.value = start[:-1] + end
            self.text_position -= 1
        elif self.is_shortcut(event, "Delete everything after cursor") and end:
            self.value = start
        elif (
            self.is_shortcut(event, "Delete everything before cursor")
            and start
        ):
            self.text_position, self.text_scroll, self.value = 0, 0, end
        elif self.is_shortcut(event, "Delete whole line") and self.value:
            self.text_position, self.text_scroll, self.value = 0, 0, ""
        elif self.is_shortcut(event, "Move cursor back") and start:
            self.text_position -= 1
        elif self.is_shortcut(event, "Move cursor forward") and end:
            self.text_position += 1
        elif self.is_shortcut(event, "Move cursor to end") and end:
            self.text_position += len(end)
        elif self.is_shortcut(event, "Move cursor to start") and start:
            self.text_position = self.text_scroll = 0
        elif self.is_shortcut(event, "Scroll cursor back") and start:
            self.text_scroll -= 1
        elif self.is_shortcut(event, "Scroll cursor forward") and end:
            self.text_scroll += 1
        elif (
            self.max_length is None or len(self.value) < self.max_length
        ) and not self.is_invalid_char(event):
            self.text_position += 1
            if self.transform_to == "lowercase":
                self.value = start + event.lower() + end
            elif self.transform_to == "uppercase":
                self.value = start + event.upper() + end
            else:
                self.value = start + event + end
        else:
            return False

        return True

    def handle_scroll(self) -> None:
        """Handle scroll & position."""
        msg: str = self.value
        offset: int = self.get_value_offset()
        if self.text_scroll <= max(0, 1 - self.text_position):
            # Scroll to start
            self.text_position += self.text_scroll
            self.text_scroll = 0
        elif self.text_position < 1:
            # Move cursor after left ellipsis
            self.text_scroll -= 1 - self.text_position
            self.text_position = 1

        max_text_position: int = len(msg) - offset - 1
        if self.text_scroll >= min(len(msg) - self.text_position - 1, offset):
            # Scroll to end
            self.text_position -= offset - self.text_scroll
            self.text_scroll = offset
        elif self.text_position > max_text_position:
            # Move cursor before right ellipsis
            self.text_scroll += self.text_position - max_text_position
            self.text_position = max_text_position

    def invalid_value(self, msg: str) -> str:
        """Validate value, return error message."""
        if len(msg) < self.min_length:
            return _("Add {0} chars").format(
                format_real(self.min_length - len(msg)),
            )

        return ""

    def is_invalid_char(self, char: str) -> bool:
        """Check if character is invalid."""
        return (
            not char.isprintable()
            or (char.isalpha() and "letters" not in self.allowed)
            or (iscategory(char, "M") and "marks" not in self.allowed)
            or (char.isnumeric() and "numbers" not in self.allowed)
            or (iscategory(char, "P") and "punctuations" not in self.allowed)
            or (char.isspace() and "separators" not in self.allowed)
            or (iscategory(char, "S") and "symbols" not in self.allowed)
            or (not char.isascii() and not self.unicode)
        ) and char.lower() not in self.whitelist

    def is_shortcut(self, event: InputEvent, key: str) -> bool:
        """Check if event is a shortcut."""
        return event.shortcut in self.shortcuts.get(key, [])

    def print_msg(self, msg: str, *, short: bool = False) -> None:
        """Print message."""
        offset: int = self.get_value_offset(short=short)
        end: str
        if short:
            if offset:
                msg = msg[:-offset - 1] + _ELLIPSIS

            raw_print(f" {cyan(msg)} ")
        elif not self.value:
            if offset:
                msg = msg[:-offset - 1] + _ELLIPSIS

            end = msg + " "
            raw_print(f" {grey(invert(end[:1]) + end[1:])}")
        else:
            self.handle_scroll()
            msg = msg[self.text_scroll:self.text_scroll + len(msg) - offset]
            if self.text_scroll:
                msg = _ELLIPSIS + msg[1:]

            if self.text_scroll < offset:
                msg = msg[:-1] + _ELLIPSIS

            start: str = msg[:self.text_position]
            end = msg[self.text_position:] + " "
            raw_print(f" {start}{invert(end[:1])}{end[1:]}")

        self.cursor.wrote(f" {msg} ")


class InputStr(BaseTextInput):
    """Class for str input."""


# pylint: disable=too-many-arguments
def input_str(  # noqa: PLR0913
    prompt: object = "",
    *,
    allowed: set[Literal[
        "letters", "marks", "numbers", "punctuations", "separators", "symbols",
    ]] | None = None,
    clear: bool = False,
    contexts: list[TerminalContext] | None = None,
    max_length: int | None = None,
    min_length: int = 0,
    placeholder: str | None = None,
    representation: type[str] = Representation,
    shortcuts: dict[str, list[str]] | None = None,
    transform_to: Literal["lowercase", "uppercase", None] = None,
    unicode: bool = True,
    value: str | None = None,
    whitelist: str = "",
) -> str | None:
    """Read str from command line input."""
    return InputStr(
        prompt,
        allowed=allowed,
        clear=clear,
        contexts=contexts,
        max_length=max_length,
        min_length=min_length,
        placeholder=placeholder,
        representation=representation,
        shortcuts=shortcuts,
        transform_to=transform_to,
        unicode=unicode,
        value=value,
        whitelist=whitelist,
    ).get_value()
