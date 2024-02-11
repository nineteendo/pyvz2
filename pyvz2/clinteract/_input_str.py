"""CLInteract class & function for str input."""
# Copyright (C) 2020-2024 Nice Zombies
# TODO(Nice Zombies): Alt + right click is disabled
# TODO(Nice Zombies): Selecting text is disabled
from __future__ import annotations

__all__: list[str] = ["BaseTextInput", "InputStr", "input_str"]
__author__: str = "Nice Zombies"

from gettext import gettext as _
from math import prod
from sys import stdout
from threading import Lock, Thread
from typing import Self, overload
from unicodedata import category

from rgbeep import (
    ColoredOutput, NoCursor, beep, cyan, grey, invert, raw_print,
    set_cursor_position,
)
from skiboard import (
    CSISequences, CtrlCodes, Event, Mouse, RawInput, SS3Sequences, ctrl, esc,
    get_event,
)

from ._classes import ContextEvent, Cursor, Representation
from ._pause import BaseInputHandler
from .real2float import format_real


# pylint: disable=too-many-instance-attributes
class BaseTextInput(BaseInputHandler[str]):
    """Base class for text input."""

    # pylint: disable=too-many-arguments, too-many-locals
    def __init__(  # noqa: PLR0913
        self: Self, prompt: object, *, allow_letters: bool = False,
        allow_marks: bool = False, allow_numbers: bool = False,
        allow_punctuations: bool = False, allow_separators: bool = False,
        allow_symbols: bool = False, ascii_only: bool = False,
        clear: bool = False, make_lowercase: bool = False,
        make_uppercase: bool = False, max_length: int = 0, min_length: int = 0,
        placeholder: object = _("Enter text..."),
        representation: type[str] = Representation,
        value: str | None = None, whitelist: str = "",
    ) -> None:
        if not (
            allow_letters or (allow_marks and not ascii_only) or allow_numbers
            or allow_punctuations or allow_separators or allow_symbols
        ) and not whitelist:
            # Allow everything when nothing is explicitly allowed
            allow_letters = allow_marks = allow_numbers = True
            allow_punctuations = allow_separators = allow_symbols = True

        err: str
        if make_lowercase and make_uppercase:
            err = "make_lowercase & make_uppercase are both True"
            raise ValueError(err)

        if min_length < 0 or (max_length and min_length > max_length):
            err = "min_length doesn't lay between 0 & max_length"
            raise ValueError(err)

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
        elif max_length and len(value) > max_length:
            err = "value is longer than max_length"
            raise ValueError(err)

        # Initialise variables for self.is_valid_char
        self.allow_letters: bool = allow_letters
        self.allow_marks: bool = allow_marks
        self.allow_numbers: bool = allow_numbers
        self.allow_punctuations: bool = allow_punctuations
        self.allow_separators: bool = allow_separators
        self.allow_symbols: bool = allow_symbols
        self.ascii_only: bool = ascii_only
        self.whitelist: str = whitelist
        invalid_char = next(
            (char for char in value if self.is_invalid_char(char)), None,
        )
        if invalid_char:
            err = f"value contains an invalid character: {invalid_char!r}"
            raise ValueError(err)

        if make_lowercase:
            value = value.lower()
        elif make_uppercase:
            value = value.upper()

        self.clear: bool = clear
        self.make_lowercase: bool = make_lowercase
        self.make_uppercase: bool = make_uppercase
        self.max_length: int = max_length
        self.text_position: int = len(value)
        self.text_scroll: int = 0
        self.min_length: int = min_length
        self.placeholder: str = representation(placeholder)
        self.lock: Lock = Lock()
        self.ready_event: ContextEvent = ContextEvent()
        self.value: str = value
        super().__init__(prompt, representation=representation)

    def display_thread(self: Self) -> None:
        """Display information on separate thread."""
        while True:
            with self.lock:
                if self.ready_event.is_set():
                    break

                msg: str = self.value if self.value else self.placeholder
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

            if self.ready_event.wait(0.1):
                break

    def enlarge_window(self: Self) -> bool:
        """Check if window is too small."""
        return self.terminal_size.columns < 2

    def get_value_offset(self: Self, *, short: bool = False) -> int:
        """Get scroll offset for value."""
        max_chars: int = prod(self.terminal_size)
        if not short:
            max_chars -= self.terminal_size.columns

        prompt_len: int = len(f"? {self.get_prompt()}")
        msg: str = self.value
        msg_len: int = len(f" {msg} ")
        return max(0, msg_len + min(prompt_len, max_chars // 2) - max_chars)

    @RawInput()
    @ColoredOutput()
    @NoCursor()
    def get_value(self: Self) -> str | None:
        with self.ready_event:
            Thread(target=self.display_thread, daemon=True).start()
            while True:
                event: Event = get_event()
                with self.lock:
                    if event.pressed and self.enlarge_window():
                        beep()
                        continue

                    if not event.pressed or self.handle_event(event):
                        self.handle_scroll()
                        continue

                    if (event.button == Mouse.BUTTON_2 or event in {
                        SS3Sequences.KEYPAD_ENTER, CtrlCodes.LINE_FEED,
                        CtrlCodes.CARRIAGE_RETURN,
                    }) and not self.invalid_value(self.value):
                        # Submit input
                        break

                    if event == CtrlCodes.ESCAPE and not self.value:
                        # Cancel
                        self.clear_screen()
                        return None

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
    def handle_event(self: Self, event: Event) -> bool:  # noqa: C901, PLR0912
        """Handle keyboard event."""
        start: str = self.value[:self.text_scroll + self.text_position]
        end: str = self.value[self.text_scroll + self.text_position:]
        if event in {
            ctrl("a"), SS3Sequences.HOME, CSISequences.HOME,
        } and start:
            # Move cursor to start of line
            self.text_position = self.text_scroll = 0
        elif event in {
            ctrl("b"), SS3Sequences.LEFT, CSISequences.LEFT,
        } and start:
            # Move cursor back one character
            self.text_position -= 1
        elif event in {ctrl("d"), CSISequences.DELETE} and end:
            # Delete character after cursor
            self.value = start + end[1:]
        elif event in {ctrl("e"), SS3Sequences.END, CSISequences.END} and end:
            # Move cursor to end of line
            self.text_position += len(end)
        elif event in {
            ctrl("f"), SS3Sequences.RIGHT, CSISequences.RIGHT,
        } and end:
            # Move cursor forward one character
            self.text_position += 1
        elif event in {ctrl("h"), CtrlCodes.DELETE} and start:
            # Delete character before cursor
            self.value = start[:-1] + end
            self.text_position -= 1
        elif event in {ctrl("k"), ctrl(CSISequences.END)} and end:
            # Delete everything after cursor
            self.value = start
        elif event == ctrl("l"):
            # Clear screen
            set_cursor_position()
            self.cursor = Cursor(self.terminal_size.columns)
        elif event in {ctrl("u"), ctrl(CSISequences.HOME)} and start:
            # Delete everything before cursor
            self.text_position, self.text_scroll, self.value = 0, 0, end
        elif event in {CtrlCodes.ESCAPE, esc("q")} and self.value:
            # Delete whole line
            self.text_position, self.text_scroll, self.value = 0, 0, ""
        elif (
            not self.max_length or len(self.value) < self.max_length
        ) and not self.is_invalid_char(event):
            if self.make_lowercase:
                event = Event(event.lower())
            elif self.make_uppercase:
                event = Event(event.upper())

            self.value = start + event + end
            self.text_position += 1
        else:
            return False

        return True

    def handle_scroll(self: Self) -> None:
        """Handle scroll and position."""
        msg: str = self.value
        offset: int = self.get_value_offset()
        if self.text_scroll <= max(0, 3 - self.text_position):
            # Scroll to start
            self.text_position += self.text_scroll
            self.text_scroll = 0
        elif self.text_position < 3:
            # Move cursor after left ellipsis
            self.text_scroll -= 3 - self.text_position
            self.text_position = 3

        max_text_position: int = len(msg) - offset - 3
        if self.text_scroll >= min(len(msg) - self.text_position - 3, offset):
            # Scroll to end
            self.text_position -= offset - self.text_scroll
            self.text_scroll = offset
        elif self.text_position > max_text_position:
            # Move cursor before right ellipsis
            self.text_scroll += self.text_position - max_text_position
            self.text_position = max_text_position

    def invalid_value(self: Self, msg: str) -> str:
        """Validate value, return error message."""
        if len(msg) < self.min_length:
            return _("Add {0} chars").format(
                format_real(self.min_length - len(msg)),
            )

        return ""

    def is_invalid_char(self: Self, char: str) -> bool:
        """Check if character is invalid."""
        return (
            not char.isprintable()
            or (char.isalpha() and not self.allow_letters)
            or (category(char).startswith("M") and not self.allow_marks)
            or (char.isnumeric() and not self.allow_numbers)
            or (category(char).startswith("P") and not self.allow_punctuations)
            or (char.isspace() and not self.allow_separators)
            or (category(char).startswith("S") and not self.allow_symbols)
            or (not char.isascii() and self.ascii_only)
        ) or char.lower() in self.whitelist

    def print_msg(self: Self, msg: str, *, short: bool = False) -> None:
        """Print message."""
        offset: int = self.get_value_offset(short=short)
        end: str
        if short:
            if offset:
                msg = "..." + msg[offset + 3:]

            raw_print("", cyan(msg), end=" ")
        elif not self.value:
            if offset:
                msg = "..." + msg[offset + 3:]

            end = msg + " "
            raw_print("", grey(invert(end[:1]) + end[1:]))
        else:
            self.handle_scroll()
            msg = msg[self.text_scroll:self.text_scroll + len(msg) - offset]
            if self.text_scroll:
                msg = "..." + msg[3:]

            if self.text_scroll < offset:
                msg = msg[:-3] + "..."

            start: str = msg[:self.text_position]
            end = msg[self.text_position:] + " "
            raw_print("", start + invert(end[:1]) + end[1:])

        self.cursor.wrote(f" {msg} ")


class InputStr(BaseTextInput):
    """Class for str input."""


# noinspection PyMissingOrEmptyDocstring
@overload
def input_str(  # pylint: disable=too-many-arguments
    prompt: object, *, ascii_only: bool = False, clear: bool = False,
    make_lowercase: bool = False, make_uppercase: bool = False,
    max_length: int = 0, min_length: int = 0,
    placeholder: object = _("Enter text..."),
    representation: type[str] = Representation, value: str | None = None,
) -> str | None:
    ...


# noinspection PyMissingOrEmptyDocstring
@overload
def input_str(  # pylint: disable=too-many-arguments, too-many-locals
    prompt: object, *, allow_letters: bool = False, allow_marks: bool = False,
    allow_numbers: bool = False, allow_punctuations: bool = False,
    allow_separators: bool = False, allow_symbols: bool = False,
    ascii_only: bool = False, clear: bool = False,
    make_lowercase: bool = False, make_uppercase: bool = False,
    max_length: int = 0, min_length: int = 0,
    placeholder: object = _("Enter text..."),
    representation: type[str] = Representation, value: str | None = None,
    whitelist: str = "",
) -> str | None:
    ...

# pylint: disable=too-many-arguments, too-many-locals


def input_str(  # noqa: PLR0913
    prompt: object, *, allow_letters: bool = False, allow_marks: bool = False,
    allow_numbers: bool = False, allow_punctuations: bool = False,
    allow_separators: bool = False, allow_symbols: bool = False,
    ascii_only: bool = False, clear: bool = False,
    make_lowercase: bool = False, make_uppercase: bool = False,
    max_length: int = 0, min_length: int = 0,
    placeholder: object = _("Enter text..."),
    representation: type[str] = Representation, value: str | None = None,
    whitelist: str = "",
) -> str | None:
    """Read str from command line input."""
    return InputStr(
        prompt, allow_letters=allow_letters, allow_marks=allow_marks,
        allow_numbers=allow_numbers, allow_punctuations=allow_punctuations,
        allow_separators=allow_separators, allow_symbols=allow_symbols,
        ascii_only=ascii_only, clear=clear, make_lowercase=make_lowercase,
        make_uppercase=make_uppercase, max_length=max_length,
        min_length=min_length, placeholder=placeholder,
        representation=representation, value=value, whitelist=whitelist,
    ).get_value()
