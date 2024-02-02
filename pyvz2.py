#!/usr/local/bin/python3
"""PyVZ2, a console utility to modify PVZ2."""
# Custom libraries
import lib.colorized
from lib.colorized import ColoredOutput
from lib.io19.input import input_event
from lib.skiboard import Event, RawInput

__all__: list[str] = []


@RawInput()  # Enable raw input for entire program
@ColoredOutput()  # Enable colored output for entire program
def main() -> None:
    """Start PyVZ2."""
    try:
        for name in [
            'alt_font', 'black', 'blink', 'blue', 'bold', 'conceal', 'cyan',
            'dim', 'double_underline', 'encircle', 'frame', 'green', 'grey',
            'invert', 'italic', 'lt_blue', 'lt_cyan', 'lt_green', 'lt_grey',
            'lt_magenta', 'lt_red', 'lt_yellow', 'magenta', 'on_black',
            'on_blue', 'on_cyan', 'on_green', 'on_grey', 'on_lt_blue',
            'on_lt_cyan', 'on_lt_green', 'on_lt_grey', 'on_lt_magenta',
            'on_lt_red', 'on_lt_yellow', 'on_magenta', 'on_red', 'on_white',
            'on_yellow', 'overline', 'rapid_blink', 'red', 'strikethrough',
            'underline', 'white', 'yellow'
        ]:
            print(getattr(lib.colorized, name)(name))
        while True:
            event: Event = input_event('Press any key...')
            print(repr(event), event.ispressed(), event.button)
    except KeyboardInterrupt:
        pass  # Hide KeyboardInterrupt


if __name__ == '__main__':
    main()
