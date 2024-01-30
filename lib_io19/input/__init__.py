"""19.io module for console input."""
# Standard libraries
import sys
from atexit import register

# Custom libraries
from ._input_event import InputEvent, input_event
from .keyboard import RawInput

__all__: list[str] = ['InputEvent']
__all__ += ['input_event']

register(RawInput.disable)
if sys.platform in ['darwin', 'linux']:
    from signal import SIGCONT, SIGTSTP, signal

    signal(SIGCONT, RawInput.resume)  # Enable raw input on resume
    signal(SIGTSTP, RawInput.suspend)  # Disable raw input on suspend
