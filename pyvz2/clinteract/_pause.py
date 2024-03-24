"""CLInteract classes & function for pausing."""
# Copyright (C) 2023-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = ["BaseInputHandler", "Pause", "pause"]
__author__: str = "Nice Zombies"

from abc import ABC, abstractmethod
from contextlib import ExitStack
from gettext import gettext as _
from math import prod
from os import get_terminal_size, terminal_size
from sys import stdin, stdout
from time import time
from typing import Generic

from ansio import TerminalContext, colored_output, no_cursor, raw_input
from ansio.colors import bold, green, red
from ansio.input import InputEvent, get_input_event
from ansio.output import (
    cursor_up, erase_in_display, raw_print, set_cursor_position,
)

from ._custom import VALUE, Cursor, Representation, get_contexts

_ELLIPSIS: str = "\u2026"


class BaseInputHandler(Generic[VALUE], ABC):
    """Base class for handling command line input."""

    def __init__(
        self,
        prompt: object = "",
        *,
        contexts: list[TerminalContext] | None = None,
        representation: type[str] = Representation,
    ) -> None:
        if contexts is None:
            contexts = get_contexts()

        self.contexts: list[TerminalContext] = contexts
        self.cursor: Cursor = Cursor(1)
        self.prompt: str = representation(prompt)
        self.representation: type[str] = representation
        self.terminal_size: terminal_size = terminal_size((1, 1))

    def print_error(self, err: str) -> None:
        """Print error message."""
        columns: int = self.terminal_size.columns
        err_len: int = len(f">> {err}")
        offset: int = max(0, err_len - columns)
        if offset:
            err = err[:-offset - 1] + _ELLIPSIS

        raw_print(red(">>"), bold(err))
        self.cursor.wrote(f">> {err}")

    def print_prompt(self, msg: str = "", *, short: bool = False) -> None:
        """Print prompt."""
        prompt: str = self.get_prompt()
        offset: int = self.get_prompt_offset(msg, short=short)
        if offset:
            prompt = prompt[:-offset - 1] + _ELLIPSIS

        raw_print(green("?"))
        self.cursor.wrote("?")
        if prompt:
            raw_print("", bold(prompt))
            self.cursor.wrote(f" {prompt}")

    def get_prompt(self) -> str:
        """Get prompt for user."""
        return self.prompt

    def get_prompt_offset(self, msg: str, *, short: bool = False) -> int:
        """Get offset for prompt."""
        max_chars: int = prod(self.terminal_size)
        if not short:
            max_chars -= self.terminal_size.columns

        prompt: str = self.get_prompt()
        prompt_len: int = len(f"? {prompt}" if prompt else "?")
        return max(
            0, prompt_len + min(len(msg), (max_chars + 1) // 2) - max_chars,
        )

    @abstractmethod
    def get_value(self) -> VALUE | None:
        """Get value from user."""

    def clear_screen(self) -> None:
        """Clear screen & reset cursor position."""
        new_terminal_size: terminal_size = get_terminal_size()
        if new_terminal_size != self.terminal_size:
            set_cursor_position()
        else:
            cursor_up(self.cursor.row)
            raw_print("\r")

        self.cursor = Cursor(new_terminal_size.columns)
        erase_in_display()
        self.terminal_size = new_terminal_size


class Pause(BaseInputHandler[None]):
    """Class for pausing."""

    def __init__(
        self,
        prompt: object = None,
        *,
        contexts: list[TerminalContext] | None = None,
        representation: type[str] = Representation,
        timeout: float | None = None,
    ) -> None:
        if prompt is None:
            if timeout is None:
                prompt = _("Press enter to continue...")
            else:
                prompt = _("Wait / Press enter to continue...")

        self.timeout: float | None = timeout
        super().__init__(
            prompt,
            contexts=contexts,
            representation=representation,
        )

    @raw_input
    @colored_output
    @no_cursor
    def get_value(self) -> None:
        if not stdin.isatty() or not stdout.isatty():
            err: str = "stdin / stdout don't refer to a terminal"
            raise RuntimeError(err)

        with ExitStack() as stack:
            for context in self.contexts:
                stack.enter_context(context)

            self.clear_screen()
            self.print_prompt(short=True)
            stdout.buffer.flush()
            start_time: float = time()
            event: InputEvent | None = get_input_event(timeout=self.timeout)
            while event and (event.moving or not event.pressed):
                if self.timeout is None:
                    event = get_input_event()
                else:
                    elapsed_time: float = time() - start_time
                    event = get_input_event(
                        timeout=self.timeout - elapsed_time,
                    )

        return self.clear_screen()


def pause(
    prompt: object = None,
    *,
    contexts: list[TerminalContext] | None = None,
    representation: type[str] = Representation,
    timeout: float | None = None,
) -> None:
    """Pause with message."""
    Pause(
        prompt,
        contexts=contexts,
        representation=representation,
        timeout=timeout,
    ).get_value()
