"""Modules."""
# Standard libraries
import sys

# pylint: disable=consider-using-in
if sys.platform == 'darwin' or sys.platform == 'linux':
    # Standard libraries
    import signal
    from signal import SIG_DFL, SIGCONT, SIGTSTP, raise_signal
    from types import FrameType
    from typing import Optional

    # Custom libraries
    from .colorized import NoCursor
    from .skiboard import RawInput

    def resume(_1: int, _2: Optional[FrameType]) -> None:
        """Resume raw input and no cursor."""
        signal.signal(SIGTSTP, suspend)
        if NoCursor.count:
            NoCursor.hide()

        if RawInput.count:
            RawInput.enable()

    signal.signal(SIGCONT, resume)  # Enable on resume

    def suspend(_1: int, _2: Optional[FrameType]) -> None:
        """Suspend raw input and no cursor."""
        NoCursor.show()
        RawInput.disable()
        signal.signal(SIGTSTP, SIG_DFL)
        raise_signal(SIGTSTP)

    signal.signal(SIGTSTP, suspend)  # Disable on suspend
