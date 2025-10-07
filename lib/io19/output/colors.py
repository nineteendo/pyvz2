"""19.io functions for colored ansi text."""
# Standard libraries
from collections.abc import Callable
from typing import Any

__all__: list[str] = [
    'alternative_font', 'black', 'blink', 'blue', 'bold', 'colored', 'conceal',
    'cyan', 'dim', 'double_underline', 'encircle', 'green', 'grey', 'invert',
    'italic', 'light_blue', 'light_cyan', 'light_green', 'light_grey',
    'light_magenta', 'light_red', 'light_yellow', 'magenta', 'on_black',
    'on_blue', 'on_cyan', 'on_green', 'on_grey', 'on_light_blue',
    'on_light_cyan', 'on_light_green', 'on_light_grey', 'on_light_magenta',
    'on_light_red', 'on_light_yellow', 'on_magenta', 'on_red', 'on_white',
    'on_yellow', 'red', 'strikethrough', 'underline', 'white', 'yellow'
]
_ESC: str = '\x1b'
_CSI: str = f'{_ESC}['


def _csi_format(start: int, sep: str, *values: Any, end: int = 0) -> str:
    """CSI formats the values."""
    return f'{_CSI}{start}m{sep.join(map(str, values))}{_CSI}{end}m'


def bold(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values in bold."""
    return _csi_format(1, sep, *values, end=22)


def dim(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values as dimmed (falls back to grey)."""
    return _csi_format(90, sep, _csi_format(2, sep, *values, end=22), end=39)


def italic(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values in italic."""
    return _csi_format(3, sep, *values, end=23)


def underline(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values as underlined."""
    return _csi_format(4, sep, *values, end=24)


def blink(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values as blinking."""
    return _csi_format(5, sep, *values, end=25)


def invert(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values as inverted."""
    return _csi_format(7, sep, *values, end=27)


def conceal(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with as concealed."""
    return _csi_format(8, sep, *values, end=28)


def strikethrough(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values in strikethrough."""
    return _csi_format(9, sep, *values, end=29)


def alternative_font(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with an alternative font."""
    return _csi_format(11, sep, *values, end=10)


def double_underline(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values as doubly underlined."""
    return _csi_format(21, sep, *values, end=24)


def black(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a black foreground color."""
    return _csi_format(30, sep, *values, end=39)


def red(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a red foreground color."""
    return _csi_format(31, sep, *values, end=39)


def green(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a green foreground color."""
    return _csi_format(32, sep, *values, end=39)


def yellow(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a yellow foreground color."""
    return _csi_format(33, sep, *values, end=39)


def blue(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a blue foreground color."""
    return _csi_format(34, sep, *values, end=39)


def magenta(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a magenta foreground color."""
    return _csi_format(35, sep, *values, end=39)


def cyan(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a cyan foreground color."""
    return _csi_format(36, sep, *values, end=39)


def light_grey(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light grey foreground color."""
    return _csi_format(37, sep, *values, end=39)


def on_black(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a black background color."""
    return _csi_format(40, sep, *values, end=49)


def on_red(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a red background color."""
    return _csi_format(41, sep, *values, end=49)


def on_green(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a green background color."""
    return _csi_format(42, sep, *values, end=49)


def on_yellow(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a yellow background color."""
    return _csi_format(43, sep, *values, end=49)


def on_blue(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a blue background color."""
    return _csi_format(44, sep, *values, end=49)


def on_magenta(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a magenta background color."""
    return _csi_format(45, sep, *values, end=49)


def on_cyan(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a cyan background color."""
    return _csi_format(46, sep, *values, end=49)


def on_light_grey(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light grey background color."""
    return _csi_format(47, sep, *values, end=49)


def encircle(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values as encircled."""
    return _csi_format(53, sep, *values, end=54)


def grey(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a grey foreground color."""
    return _csi_format(90, sep, *values, end=39)


def light_red(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light red foreground color."""
    return _csi_format(91, sep, *values, end=39)


def light_green(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light green foreground color."""
    return _csi_format(92, sep, *values, end=39)


def light_yellow(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light yellow foreground color."""
    return _csi_format(93, sep, *values, end=39)


def light_blue(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light blue foreground color."""
    return _csi_format(94, sep, *values, end=39)


def light_magenta(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light magenta foreground color."""
    return _csi_format(95, sep, *values, end=39)


def light_cyan(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light cyan foreground color."""
    return _csi_format(96, sep, *values, end=39)


def white(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a white foreground color."""
    return _csi_format(97, sep, *values, end=39)


def on_grey(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a grey background color."""
    return _csi_format(100, sep, *values, end=49)


def on_light_red(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light red background color."""
    return _csi_format(101, sep, *values, end=49)


def on_light_green(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light green background color."""
    return _csi_format(102, sep, *values, end=49)


def on_light_yellow(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light yellow background color."""
    return _csi_format(103, sep, *values, end=49)


def on_light_blue(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light blue background color."""
    return _csi_format(104, sep, *values, end=49)


def on_light_magenta(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light magenta background color."""
    return _csi_format(105, sep, *values, end=49)


def on_light_cyan(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a light cyan background color."""
    return _csi_format(106, sep, *values, end=49)


def on_white(*values: Any, sep: str = ' ') -> str:
    """ANSI formats the values with a white background color."""
    return _csi_format(107, sep, *values, end=49)


def colored(
    functions: list[Callable[..., str]], *values: Any, sep: str = ' '
) -> str:
    """ANSI formats the values using the provided functions."""
    text: str = sep.join(map(str, values))
    for function in functions:
        text = function(text)

    return text
