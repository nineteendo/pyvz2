"""SorText module for sorting text."""
# Copyright (C) 2023-2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = ["natsort", "natsort_key", "natsorted"]

from re import findall
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


class _NatChar:
    """Class for natural sortable characters.

    Order: letter > number > rest
    """

    def __init__(self, char: str) -> None:
        """Make new NatString instance."""
        self.value: int | str
        if char.isdigit():
            self.value = int(char)
        elif len(char) != 1:
            err: str = "non numbers must have a length of 1"
            raise ValueError(err)
        else:
            self.value = char.lower()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _NatChar) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, _NatChar):
            return NotImplemented

        if isinstance(self.value, int):
            if isinstance(other.value, int):
                return self.value < other.value

            return other.value.isalpha()

        if isinstance(other.value, int):
            return not self.value.isalpha()

        if self.value.isalpha() == other.value.isalpha():
            return self.value < other.value

        return other.value.isalpha()


def natsort_key(string: str) -> tuple[_NatChar, ...]:
    """Split string in natural sortable characters."""
    return tuple(map(_NatChar, findall(r"\D|\d+", string)))


def natsort(lst: list[str], *, reverse: bool = False) -> None:
    """Sort a list of strings naturally."""
    lst.sort(key=natsort_key, reverse=reverse)


def natsorted(lst: Iterable[str], *, reverse: bool = False) -> list[str]:
    """Sort an iterable of strings naturally."""
    return sorted(lst, key=natsort_key, reverse=reverse)
