"""19.io module for console input."""
# Standard libraries
import sys
from atexit import register

# Custom libraries
from ._input_event import input_event
from .keyboard import RawInput

__all__: list[str] = ['input_event']

register(RawInput.disable)
# pylint: disable=consider-using-in
if sys.platform == 'darwin' or sys.platform == 'linux':
    # pylint: disable=no-name-in-module
    from signal import SIGCONT, SIGTSTP, signal

    signal(SIGCONT, RawInput.resume)  # Enable raw input on resume
    signal(SIGTSTP, RawInput.suspend)  # Disable raw input on suspend
