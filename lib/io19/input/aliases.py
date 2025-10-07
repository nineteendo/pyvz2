"""19.io type aliases for command line input."""
# Custom libraries
from ._input_bytes import BytesOrHex
from ._input_datetime import RelativeDate, RelativeDateTime, RelativeTime
from ._input_path import Extensions, Prefixes

__all__: list[str] = [
    'BytesOrHex', 'Extensions', 'Prefixes', 'RelativeDate', 'RelativeDateTime',
    'RelativeTime'
]
