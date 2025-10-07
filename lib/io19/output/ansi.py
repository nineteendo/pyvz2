"""19.io functions for ansi sequences."""
__all__: list[str] = [
    'cursor_horizontal_absolute', 'cursor_up', 'erase_in_display',
    'erase_in_line', 'set_cursor_position'
]
_ESC: str = '\x1b'
_CSI: str = f'{_ESC}['


def cursor_up(characters: int = 1) -> None:
    """Move cursor up."""
    if characters > 0:
        print(end=f'{_CSI}{characters}A')
    elif characters < 0:
        print(end=f'{_CSI}{-characters}B')


def cursor_horizontal_absolute(column: int = 1) -> None:
    """Move cursor to column n."""
    print(end=f'{_CSI}{column}G')


def set_cursor_position(row: int = 0, column: int = 0) -> None:
    """Set cursor position."""
    print(end=f'{_CSI}{row};{column}H')


def erase_in_display(mode: int = 0) -> None:
    """Erase in display."""
    print(end=f'{_CSI}{mode}J')


def erase_in_line(mode: int = 0) -> None:
    """Erase in line."""
    print(end=f'{_CSI}{mode}K')
