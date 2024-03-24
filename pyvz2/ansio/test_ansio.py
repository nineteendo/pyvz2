"""AnsI/O tests."""
# Copyright (C) 2024 Nice Zombies
from __future__ import annotations

__all__: list[str] = []
__author__: str = "Nice Zombies"

from .colors import bold
from .input import InputEvent


def test_make_formatter() -> None:
    """Test _make_formatter."""
    # ansi formatting
    assert bold() == "\x1b[1m\x1b[22m"
    assert bold("foo") == "\x1b[1mfoo\x1b[22m"
    # separator
    assert bold("foo", "bar") == "\x1b[1mfoo bar\x1b[22m"
    assert bold("foo", "bar", sep=",") == "\x1b[1mfoo,bar\x1b[22m"


def get_shortcut(string: str) -> str:
    """Get shortcut."""
    return InputEvent(string).shortcut


def test_input_event_shortcut_keyboard() -> None:
    """Test InputEvent.shortcut for keyboard."""
    # alt+shift+letter
    assert get_shortcut("\x1bA") == "alt+shift+a"
    # alt
    assert get_shortcut("\x1ba") == "alt+a"
    assert get_shortcut("\x1b\x1bOA") == "alt+up"
    assert get_shortcut("\x1b\x1b[A") == "alt+up"
    # ctrl+letter
    assert get_shortcut("\x00") == "ctrl+@"
    assert get_shortcut("\x01") == "ctrl+a"
    assert get_shortcut("\x08") == "ctrl+h"
    assert get_shortcut("\t") == "tab"  # Exception
    assert get_shortcut("\n") == "enter"  # Exception
    assert get_shortcut("\x0b") == "ctrl+k"
    assert get_shortcut("\x0c") == "ctrl+l"
    assert get_shortcut("\r") == "enter"  # Exception
    assert get_shortcut("\x0e") == "ctrl+n"
    assert get_shortcut("\x1a") == "ctrl+z"
    assert get_shortcut("\x1b") == "escape"  # Exception
    assert get_shortcut("\x1c") == "ctrl+\\"
    assert get_shortcut("\x1d") == "ctrl+]"
    assert get_shortcut("\x1e") == "ctrl+^"
    assert get_shortcut("\x1f") == "ctrl+_"
    # keyboard modifier
    assert get_shortcut("\x1b[1;2A") == "shift+up"
    assert get_shortcut("\x1b[1;3A") == "alt+up"
    assert get_shortcut("\x1b[1;4A") == "alt+shift+up"
    assert get_shortcut("\x1b[1;5A") == "ctrl+up"
    assert get_shortcut("\x1b[1;6A") == "ctrl+shift+up"
    assert get_shortcut("\x1b[1;7A") == "ctrl+alt+up"
    assert get_shortcut("\x1b[1;8A") == "ctrl+alt+shift+up"
    assert get_shortcut("\x1b[1;9A") == "meta+up"
    assert get_shortcut("\x1b[1;10A") == "shift+meta+up"
    assert get_shortcut("\x1b[1;11A") == "alt+meta+up"
    assert get_shortcut("\x1b[1;12A") == "alt+shift+meta+up"
    assert get_shortcut("\x1b[1;13A") == "ctrl+meta+up"
    assert get_shortcut("\x1b[1;14A") == "ctrl+shift+meta+up"
    assert get_shortcut("\x1b[1;15A") == "ctrl+alt+meta+up"
    assert get_shortcut("\x1b[1;16A") == "ctrl+alt+shift+meta+up"
    assert get_shortcut("\x1b[1;2S") == "shift+f4"
    assert get_shortcut("\x1b[1;2~") == "shift+home"  # Exception
    assert get_shortcut("\x1b[2;2~") == "shift+insert"
    # shift+tab
    assert get_shortcut("\x1b[Z") == "shift+tab"
    # case insensitive
    assert get_shortcut("A") == "a"


def test_input_event_shortcut_mouse() -> None:
    """Test InputEvent.shortcut for mouse."""
    # sgr mouse
    assert get_shortcut("\x1b[<0;1;1M") == "primary_click"
    assert get_shortcut("\x1b[<0;1;1m") == "primary_click"
    # mouse
    assert get_shortcut("\x1b[M !!") == "primary_click"
    # mouse modifier
    assert get_shortcut("\x1b[<4;1;1M") == "shift+primary_click"
    assert get_shortcut("\x1b[<8;1;1M") == "alt+primary_click"
    assert get_shortcut("\x1b[<12;1;1M") == "alt+shift+primary_click"
    assert get_shortcut("\x1b[<16;1;1M") == "ctrl+primary_click"
    assert get_shortcut("\x1b[<20;1;1M") == "ctrl+shift+primary_click"
    assert get_shortcut("\x1b[<24;1;1M") == "ctrl+alt+primary_click"
    assert get_shortcut("\x1b[<28;1;1M") == "ctrl+alt+shift+primary_click"


def ismoving(string: str) -> bool:
    """Is moving."""
    return InputEvent(string).moving


def test_input_event_moving() -> None:
    """Test InputEvent.moving."""
    # mouse
    assert not ismoving("\x1b[M !!")
    assert ismoving("\x1b[M@!!")
    # sgr mouse
    assert not ismoving("\x1b[<0;1;1M")
    assert ismoving("\x1b[<32;1;1M")
    # normal
    assert not ismoving("a")


def ispressed(string: str) -> bool:
    """Is pressed."""
    return InputEvent(string).pressed


def test_input_event_pressed() -> None:
    """Test InputEvent.pressed."""
    # mouse
    assert ispressed("\x1b[M !!")
    assert not ispressed("\x1b[M#!!")
    # sgr mouse
    assert ispressed("\x1b[<0;1;1M")
    assert not ispressed("\x1b[<0;1;1m")
    assert not ispressed("\x1b[<35;1;1M")
    # normal
    assert ispressed("a")
