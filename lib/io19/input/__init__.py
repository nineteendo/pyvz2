"""
19.io sub module for command line input.

Python 3.8- is not supported & won't receive bug fixes.
"""
# Linting arguments
# mypy: disable-error-code="attr-defined, assignment, misc"
# pylint: disable=useless-suppression
# ...
# pylint: disable=no-name-in-module, too-many-branches

# Standard libraries
import atexit
from datetime import timedelta
from enum import Enum
from locale import LC_ALL, setlocale
from os.path import join
from platform import system
from typing import Optional

# Custom libraries
from ..output.ansi import erase_in_display, set_cursor_position
from ..translate import gettext as _
from ._classes import Exit, Info, Unique
from ._input_bytes import input_bytes, input_str
from ._input_complex import input_bool, input_complex, input_float, input_int
from ._input_datetime import (input_date, input_datetime, input_time,
                              input_timedelta)
from ._input_enum import (category, dict_picker, entities, identity,
                          input_enum, sequence_picker)
from ._input_event import input_event
from ._input_path import config_picker, input_path
from .keyboard import RawInput

__all__: list[str] = ['Exit', 'Info', 'Unique']
__all__ += [
    'category', 'config_picker', 'demo', 'dict_picker', 'entities', 'identity',
    'input_bool', 'input_bytes', 'input_complex', 'input_date',
    'input_datetime', 'input_enum', 'input_event', 'input_float', 'input_int',
    'input_path', 'input_str', 'input_time', 'input_timedelta',
    'sequence_picker', 'shortcuts'
]


class _Color(Enum):
    """Enum test class."""

    RED = 1
    GREEN = 2
    BLUE = 3


def shortcuts() -> None:
    """Display a list of all shortcuts."""
    dict_picker(_('Keyboard shortcuts'), {
        'Bs':         _('Delete character before cursor'),
        'Cmd+Bs':     _('Delete everything before cursor'),
        'Cmd+Lt':     _('Move cursor to start of line'),
        'Cmd+Rt':     _('Move cursor to end of line'),
        **category(_('Ctrl shortcuts')),
        'Ctrl+A':     _('Move cursor to start of line'),
        'Ctrl+B':     _('Move cursor back one character'),
        'Ctrl+Break': _('Force quit'),
        'Ctrl+C':     _('Force quit'),
        'Ctrl+D':     _('Delete character after cursor'),
        'Ctrl+E':     _('Move cursor to end of line'),
        'Ctrl+F':     _('Move cursor forward one character'),
        'Ctrl+H':     _('Delete character before cursor'),
        'Ctrl+Home':  _('Delete everything before cursor'),
        'Ctrl+I':     _('Complete input / Select next option'),
        'Ctrl+J':     _('Submit input'),
        'Ctrl+K':     _('Delete everything after cursor'),
        'Ctrl+L':     _('Clear screen'),
        'Ctrl+M':     _('Submit input'),
        'Ctrl+R':     _('Refresh screen'),
        'Ctrl+T':     _('Swap character before & after cursor'),
        'Ctrl+U':     _('Delete everything before cursor'),
        'Ctrl+W':     _('Delete word before cursor'),
        'Ctrl+Y':     _('Suspend execution'),
        'Ctrl+Z':     _('Suspend execution'),
        **category(''),
        'Delete':     _('Delete character after cursor'),
        'Dn':         _('Select next option'),
        'Enter':      _('Submit input'),
        'Escape':     _('Delete whole line (Cancel when empty)'),
        'Fn+Bs':      _('Delete character after cursor'),
        'Fn+Ctrl+Lt': _('Delete everything before cursor'),
        'Lt':         _('Move cursor back one character'),
        **category(_('Meta shortcuts')),
        'Meta+B':     _('Move cursor back one word'),
        'Meta+Bs':    _('Delete word before cursor'),
        'Meta+C':     _('Capitalize word after cursor'),
        'Meta+D':     _('Delete word after cursor'),
        'Meta+F':     _('Move cursor forward one word'),
        'Meta+L':     _('Make word after cursor lowercase'),
        'Meta+Lt':    _('Move cursor back one word'),
        'Meta+Rt':    _('Move cursor forward one word'),
        'Meta+Sc-Dn': _('Go to next options page'),
        'Meta+Sc-Up': _('Go to previous options page'),
        'Meta+U':     _('Make word after cursor uppercase'),
        **category(''),
        'Mid-Click':  _('Submit input'),
        'Rt':         _('Move cursor forward one character'),
        'Sc-Dn':      _('Scroll options one down'),
        'Sc-Up':      _('Scroll options one up'),
        'Shift+Tab':  _('Select previous option'),
        'Tab':        _('Complete input / Select next option'),
        'Up':         _('Select previous option'),
        **category(_('Volume down shortcuts')),
        'Vol-Dn+A':   _('Move cursor to start of line'),
        'Vol-Dn+B':   _('Move cursor back one character'),
        'Vol-Dn+C':   _('Force quit'),
        'Vol-Dn+D':   _('Delete character after cursor'),
        'Vol-Dn+E':   _('Move cursor to end of line'),
        'Vol-Dn+F':   _('Move cursor forward one character'),
        'Vol-Dn+H':   _('Delete character before cursor'),
        'Vol-Dn+I':   _('Complete input / Select next option'),
        'Vol-Dn+J':   _('Submit input'),
        'Vol-Dn+K':   _('Delete everything after cursor'),
        'Vol-Dn+L':   _('Clear screen'),
        'Vol-Dn+M':   _('Submit input'),
        'Vol-Dn+R':   _('Refresh screen'),
        'Vol-Dn+T':   _('Swap character before & after cursor'),
        'Vol-Dn+U':   _('Delete everything before cursor'),
        'Vol-Dn+W':   _('Delete word before cursor'),
        'Vol-Dn+Y':   _('Suspend execution'),
        'Vol-Dn+Z':   _('Suspend execution'),
        **category(_('Volume up shortcuts')),
        'Vol-Up+A':   _('Move cursor back one character'),
        'Vol-Up+D':   _('Move cursor forward one character'),
        'Vol-Up+E':   _('Delete whole line (Cancel when empty)'),
        'Vol-Up+S':   _('Select next option'),
        'Vol-Up+T':   _('Complete input / Select next option'),
        'Vol-Up+W':   _('Select previous option'),
        'Vol-Up+X':   _('Delete character after cursor')
    }, clear=True)


def demo() -> None:  # noqa: MC0001
    """Show demo of io19."""
    function: Optional[str] = None
    while True:
        function = dict_picker(_('Demo'), {
            'a':  Info('Simple input'),  # Entering text
            'a0': 'Input `Event`',
            'a1': 'Input `bool`',
            'a2': 'Input `bytes`',
            'a3': 'Input `complex`',
            'a4': 'Input `float`',
            'a5': 'Input `int`',
            'a6': 'Input `str`',
            'b':  Info('Complex input'),  # Selecting from a list
            'b0': 'Input `Enum`',
            'b1': 'Input `Path`',
            'b2': 'Input `date`',
            'b3': 'Input `datetime`',
            'b4': 'Input `time`',
            'b5': 'Input `timedelta`',
            'c':  Info('Special input'),  # Miscellaneous
            'c0': 'Dict picker',
            'c1': 'Sequence picker',
            'c2': 'Config picker',
            'd':  Info(_('Back')),
            'd0': Exit(_('Back'))
        }, clear=True, value=function)
        if function is None or isinstance(function, Exit):
            set_cursor_position()
            return erase_in_display()

        if function == 'Input `Event`':
            print(input_event('Press any key:'))
        elif function == 'Input `bool`':
            print(input_bool('Select truth value:', value=True))
        elif function == 'Input `bytes`':
            print(input_bytes('Enter bytes:', value=b'abcd'))
        elif function == 'Input `complex`':
            print(input_complex(
                'Enter a complex number (real part):', value=1.2 + 3.4j)
            )
        elif function == 'Input `float`':
            print(input_float('Enter a decimal number:', value=12.34))
        elif function == 'Input `int`':
            print(input_int('Enter a whole number:', value=1234))
        elif function == 'Input `str`':
            print(input_str('Enter a string:', value='abcd'))
        elif function == 'Input `Enum`':
            print(input_enum('Enter an enum value:', _Color.GREEN))
        elif function == 'Input `Path`':
            print(input_path('Select a path:', 'pyvz2.py'))
        elif function == 'Input `date`':
            print(input_date('Select date (year):', value=timedelta()))
        elif function == 'Input `datetime`':
            print(input_datetime(
                'Select datetime (year):', value=timedelta())
            )
        elif function == 'Input `time`':
            print(input_time('Select time (hour):', value=timedelta()))
        elif function == 'Input `timedelta`':
            print(input_timedelta('Select timedelta (days):', value=timedelta(
                67, 45, minutes=23, hours=12
            )))
        elif function == 'Dict picker':
            print(dict_picker('Select an option:', {
                0: 'Option zero',
                1: 'Option one',
                2: 'Option two',
                3: 'Option three',
                4: 'Option four',
                5: 'Option five',
                6: 'Option six',
                7: 'Option seven',
                8: 'Option eight',
                9: 'Option nine'
            }, key=5))
        elif function == 'Sequence picker':
            print(sequence_picker('Select an option:', [
                f'Option {i}' for i in range(10)
            ], value='Option 5'))
        elif function == 'Config picker':
            print(config_picker('Select config:', join(
                'configs', 'demo'), 0, fields=1))


atexit.register(RawInput.disable)
setlocale(LC_ALL, '')  # NOTE - Enable locale
if system() in ['Darwin', 'Linux']:
    from signal import SIGTSTP, signal

    from .keyboard import suspend

    signal(SIGTSTP, suspend)  # NOTE - Disable raw input on suspend
