"""
19.io sub module for command line output.

Python 3.8- is not supported & won't receive bug fixes.
"""
# Standard libraries
from os import system

__all__: list[str] = []

# HACK - Enable colors on Windows 10
system('')  # nosec B605 B607
