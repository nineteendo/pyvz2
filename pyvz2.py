#!/usr/local/bin/python3
"""PyVZ2, a console utility to modify PVZ2."""
# Custom libraries
from lib.colorized import ColoredOutput
from lib.io19.input import pause
from lib.skiboard import RawInput

__all__: list[str] = []


@RawInput()  # Enable raw input for entire program
@ColoredOutput()  # Enable colored output for entire program
def main() -> None:
    """Start PyVZ2."""
    try:
        pause()
    except KeyboardInterrupt:
        pass  # Hide KeyboardInterrupt


if __name__ == '__main__':
    main()
