#!/usr/local/bin/python3
"""PyVZ2, a console utility to modify PVZ2."""
# Custom libraries
from lib_io19.input.keyboard import Event, RawInput, get_event

__all__: list[str] = []


@RawInput()  # Enable raw input for entire program
def main() -> None:
    """Start PyVZ2."""
    try:
        while True:
            event: Event = get_event()
            print(repr(event), event.ispressed(), event.button)
    except KeyboardInterrupt:
        pass  # Hide KeyboardInterrupt


if __name__ == '__main__':
    main()
