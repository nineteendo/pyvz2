"""
19.io module for working with command-line input & output.

Python 3.8- is not supported & won't receive bug fixes.
"""
# Standard libraries
from typing import Optional

# Custom libraries
from .input import input_path
from .input.aliases import Prefixes
from .input.classes import Representation
from .path import StrOrBytesPath
from .translate import gettext as _

__all__: list[str] = ['open_path']


def open_path(
    cwd: StrOrBytesPath, *, all_dirs: bool = True,
    hidden_prefixes: Prefixes = ('.', '$', '~$'),
    home: Optional[StrOrBytesPath] = None, make_lowercase: bool = False,
    make_uppercase: bool = False, placeholder: Optional[str] = None,
    representation: type[str] = Representation, show_broken_links: bool = True,
    show_hidden_items: bool = False, sub_dirs: bool = True
) -> None:
    """File manager controlled with console input."""
    input_path(
        _('cwd'), cwd, all_dirs=all_dirs, allow_chmod=True, allow_copy=True,
        allow_create=True, allow_delete=True, allow_move=True, allow_open=True,
        allow_rename=True, clear=True, hidden_prefixes=hidden_prefixes,
        home=home, make_lowercase=make_lowercase,
        make_uppercase=make_uppercase, placeholder=placeholder,
        representation=representation, show_broken_links=show_broken_links,
        show_hidden_items=show_hidden_items, show_special=True,
        sub_dirs=sub_dirs
    )
