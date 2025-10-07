"""19.io functions for dealing with paths.

Fixes issues with built-in path functions
Defines new path functions
"""
# TODO - Implement winmove2trash & linuxmove2trash

# Linting arguments
# mypy: disable-error-code=attr-defined
# pylint: disable=useless-suppression
# ...
# pylint: disable=no-name-in-module, ungrouped-imports, too-many-branches

# Standard libraries
import sys
from collections.abc import Sequence
from errno import EACCES
from os import (
    R_OK, W_OK, X_OK, PathLike, access, chdir, curdir, fsdecode, fspath,
    getcwd,
)
from os import listdir as _listdir
from os import readlink, sep, stat
from os.path import abspath
from os.path import commonpath as _commonpath
from os.path import dirname, exists, isabs, isdir, islink, join
from os.path import realpath as _realpath
from os.path import relpath as _relpath
from os.path import splitdrive
from platform import system
from stat import S_ISFIFO, S_ISSOCK, S_ISWHT
from subprocess import CompletedProcess  # nosec B404
from subprocess import run as _run  # nosec B404
from sys import executable
from sys import path as syspath
from sys import version_info
from typing import Any, AnyStr, Optional, Union, overload

__all__: list[str] = ["DEFROOT"]
__all__ += ["BytesPath", "GenericPath", "StrOrBytesPath", "StrPath"]
__all__ += [
    "commonpath",
    "edit",
    "get_quotes",
    "get_special_characters",
    "isexecutable",
    "isfifo",
    "ishidden",
    "isjunction",
    "isreadable",
    "isroot",
    "issocket",
    "isvalid",
    "iswhiteout",
    "iswriteable",
    "junction",
    "link",
    "listdir",
    "mkfifo",
    "move2trash",
    "process_path",
    "realpath",
    "relpath",
    "run",
    "use_main_dir",
]
_ALLOW_MOVE2TRASH: bool = True
_HIDE_NO_X: bool = True

DEFROOT: str

StrPath = Union[str, PathLike[str]]
BytesPath = Union[bytes, PathLike[bytes]]
GenericPath = Union[AnyStr, PathLike[AnyStr]]
StrOrBytesPath = Union[StrPath, BytesPath]
FileDescriptorOrPath = Union[StrOrBytesPath, int]

if system() == "Windows":
    from stat import FILE_ATTRIBUTE_HIDDEN

    DEFROOT = "c:\\"

    def edit(path: StrOrBytesPath) -> None:
        """Open in default program."""
        run(["start", fsdecode(path)], shell=True)  # nosec B604

    def commonpath(paths: Sequence[StrPath]) -> str:
        """Given a sequence of path names, returns the longest common sub-path.

        Fixes paths on a different drive
        """
        if not paths:
            return _commonpath(paths)

        paths = list(map(fsdecode, paths))
        drive: str = splitdrive(paths[0])[0].lower()
        if any(splitdrive(path)[0].lower() != drive for path in paths):
            return ""

        return _commonpath(paths)

    def ishidden(path: StrOrBytesPath) -> bool:
        """Test whether a path is hidden."""
        try:
            st_: stat_result = stat(path)
        except (OSError, ValueError):
            return False

        return (
            not isroot(path) and
            bool(st_.st_file_attributes & FILE_ATTRIBUTE_HIDDEN)
        )

    def junction(src: StrOrBytesPath, dst: StrOrBytesPath) -> None:
        """Make junction."""
        if not isabs(src):
            raise ValueError("source must be absolute")

        if not isdir(src):
            raise ValueError("source must be a directory")

        run(["mklink", "/j", fsdecode(dst), fsdecode(src)], shell=True)

    # noinspection PyUnusedLocal

    def mkfifo(
        path: StrOrBytesPath, mode: int = 0o666, *,
        dir_fd: Optional[int] = None,
    ) -> None:
        """Make FIFO (named pipe)."""
        raise OSError("System doesn't support FIFO's (named pipes)")

    def move2trash(path: StrOrBytesPath) -> bool:
        """Move file / directory to trash."""
        fspath(path)
        return False
elif system() in ["Darwin", "Linux"]:
    from os import mkfifo as _mkfifo
    from os import symlink

    DEFROOT = sep

    def junction(src: StrOrBytesPath, dst: StrOrBytesPath) -> None:
        """Make junction."""
        if not isabs(src):
            raise ValueError("source must be absolute")

        if not isdir(src):
            raise ValueError("source must be a directory")

        symlink(src, dst)

    mkfifo = _mkfifo

    def commonpath(paths: Sequence[StrPath]) -> str:
        """Given a sequence of path names, returns the longest common sub-path.

        Fixes single slash for double slashed paths
        """
        newpaths: list[str] = list(map(fsdecode, paths))
        if not all(path.startswith(sep + sep) for path in newpaths):
            return _commonpath(newpaths)

        # Paths all start with sep + sep
        return sep + _commonpath(newpaths)

    if system() == "Darwin":
        from datetime import datetime
        from os.path import basename, expanduser
        from shutil import move
        from stat import UF_HIDDEN

        def edit(path: StrOrBytesPath) -> None:
            """Open in default program."""
            run(["open", fsdecode(path)])

        def ishidden(path: StrOrBytesPath) -> bool:
            """Test whether a path is hidden."""
            try:
                st_: stat_result = stat(path)
            except (OSError, ValueError):
                return False

            return bool(st_.st_flags & UF_HIDDEN)

        def move2trash(path: StrOrBytesPath) -> bool:
            """Move file / directory to trash."""
            if not _ALLOW_MOVE2TRASH:
                return False

            destination: str = join(
                expanduser("~"), ".Trash", basename(fsdecode(path)),
            )
            if exists(destination) or islink(destination):
                destination += f' {datetime.now().strftime("%H.%M.%S")}'

            if exists(destination):
                # Just stop trashing files for all seconds of next minute
                return False

            move(fsdecode(path), destination)
            return True
    else:
        def edit(path: StrOrBytesPath) -> None:
            """Open in default program."""
            run(["xdg-open", fsdecode(path)])

        def ishidden(path: StrOrBytesPath) -> bool:
            """Test whether a path is hidden."""
            path = fspath(path)
            if isinstance(path, bytes):
                prefix = b"."
            else:
                prefix = "."

            return basename(path).startswith(prefix)

        def move2trash(path: StrOrBytesPath) -> bool:
            """Move file / directory to trash."""
            fspath(path)
            return False
else:
    raise RuntimeError(f"Unsupported operating system: {system()!r}")


def get_quotes() -> dict[str, str]:
    """Get quotes."""
    return {
        # start: end
        '"': '"',
        "'": "'",
    }


def get_special_characters(quotes: dict[str, str]) -> set[str]:
    """Get special characters."""
    return set(
        ["\\", " ", "(", ")"] + list(quotes.keys()) + list(quotes.values()),
    )


def isexecutable(path: FileDescriptorOrPath) -> bool:
    """Test whether a path is executable."""
    return access(path, X_OK)


def isfifo(path) -> bool:
    """Test whether a path is a FIFO (named pipe)."""
    try:
        st_ = stat(path)
    except (OSError, ValueError):
        return False

    return S_ISFIFO(st_.st_mode)


if version_info >= (3, 12):
    # noinspection PyUnresolvedReferences
    from os.path import isjunction as _isjunction
elif system() == "Windows":
    from os import lstat, stat_result
    from stat import IO_REPARSE_TAG_MOUNT_POINT

    def _isjunction(path: StrOrBytesPath) -> bool:
        """Test whether a path is a junction."""
        try:
            st_: stat_result = lstat(path)
        except (OSError, ValueError):
            return False

        return st_.st_reparse_tag == IO_REPARSE_TAG_MOUNT_POINT
else:
    def _isjunction(path: StrOrBytesPath) -> bool:
        """Test whether a path is a junction."""
        fspath(path)
        return False

isjunction = _isjunction


def isreadable(path: FileDescriptorOrPath) -> bool:
    """Test whether a path is readable."""
    return access(path, R_OK)


def isroot(path: StrOrBytesPath) -> bool:
    """Test whether a path is a root."""
    return abspath(path) == dirname(abspath(path))


def issocket(path: StrOrBytesPath) -> bool:
    """Test whether a path is a socket file."""
    try:
        st_ = stat(path)
    except (OSError, ValueError):
        return False

    return S_ISSOCK(st_.st_mode)


def isvalid(path: StrOrBytesPath) -> bool:
    r"""Test whether a path is valid.

    macOS:

    - New file: `newfile.txt` -> FileNotFoundError -> valid
    - Under a file: `foo.txt/bar.txt` -> NotADirectoryError -> invalid
    - Too long file name: `"a" * 256` -> OSError -> invalid
    - Too long path: `"a/" * 512` -> OSError -> invalid
    - Too many levels of symlinks: `"s/" * 33` -> OSError -> invalid

    Windows:

    - New file: `newfile.txt` -> FileNotFoundError -> valid
    - Under a file: `foo.txt/bar` -> FileNotFoundError -> valid (**WRONG!**)
    - Too long file name: `"a" * 256` -> OSError -> invalid
    - Too long path: `("a" * 255 + "\\") * 128` -> ValueError -> invalid
    - Too many levels of symlinks: `"s\\" * 64` -> OSError -> invalid
    - Incorrect name: `\foo` -> OSError -> invalid
    - Incorrect name: `foo*bar` -> OSError -> invalid
    - Name ending with period: `foo.` -> valid (**WRONG!**)
    - Name ending with space: `foo ` -> valid (**WRONG!**)
    - File stream: `foo:bar` -> valid (**WRONG!**)
    - Character device: `nul` -> valid (*WRONG?*)
    - DOS device name: `aux` -> valid
    - DOS device name with extension: `nul.txt` -> valid
    """
    try:
        stat(path)
    except FileNotFoundError:
        return True
    except (OSError, ValueError):
        return False

    return True


def iswhiteout(path: StrOrBytesPath) -> bool:
    """Test whether a path is a whiteout."""
    try:
        st_ = stat(path)
    except (OSError, ValueError):
        return False

    return S_ISWHT(st_.st_mode)


def iswriteable(path: FileDescriptorOrPath) -> bool:
    """Test whether a path is writeable."""
    return access(path, W_OK)


try:
    from os import link as _link
except ImportError:
    # noinspection PyUnusedLocal
    def _link(
        src: StrOrBytesPath, dst: StrOrBytesPath, *,
        src_dir_fd: Optional[int] = None, dst_dir_fd: Optional[int] = None,
        follow_symlinks: bool = True,
    ) -> None:
        """Make hardlink."""
        raise OSError("System doesn't support hard links")

link = _link


@overload
def listdir(path: Optional[StrPath] = None) -> list[str]:
    """List items in directory.

    Raise permission error for inaccesible dirs
    """


@overload
def listdir(path: BytesPath) -> list[bytes]:
    """List items in directory.

    Raise permission error for inaccesible dirs
    """


@overload
def listdir(path: int) -> list[str]:
    """List items in directory.

    Raise permission error for inaccesible dirs
    """


def listdir(path: Optional[FileDescriptorOrPath] = None) -> Union[
    list[bytes], list[str],
]:
    """List items in directory.

    Raise permission error for inaccesible dirs
    """
    if path is None:
        path = curdir

    if isdir(path) and not isexecutable(path) and _HIDE_NO_X:
        # Hide r-- & rw-
        raise PermissionError(EACCES, "Permission denied", path)

    return _listdir(path)


def process_path(
    escaped_path: str, quotes: Optional[dict[str, str]] = None,
    special_characters: Optional[set[str]] = None,
) -> str:
    """Process hybrid path."""
    character: str
    end_quotation: str = ""
    escaped: bool = False
    if quotes is None:
        quotes = get_quotes()

    if special_characters is None:
        special_characters = get_special_characters(quotes)

    temp_spaces: int = 0
    unescaped_path: str = ""
    for character in escaped_path:
        if escaped or character != "":
            unescaped_path += " " * temp_spaces
            temp_spaces = 0

        if escaped:
            if character in special_characters:
                unescaped_path += character
            else:
                unescaped_path += "\\" + character

            escaped = False
        elif character == "\\":
            escaped = True
        elif character == end_quotation:
            end_quotation = ""
        elif end_quotation:
            unescaped_path += character
        elif character in quotes:
            end_quotation = quotes[character]
        elif character == "":
            temp_spaces += 1
        else:
            unescaped_path += character

    if escaped:
        unescaped_path += "\\"

    return unescaped_path


def realpath(path: AnyStr) -> AnyStr:
    """Get path without Symlinks.

    Fixes getting realpath of broken junction or secret symlink
    """
    try:
        return _realpath(path)
    except NotADirectoryError:
        # Broken junction
        return readlink(path)
    except PermissionError:
        # Secret symlink
        return abspath(path)


def relpath(path: StrPath, start: Optional[StrPath] = None) -> str:
    """Return a relative version of a path.

    Fixes paths on a different drive
    """
    path = fsdecode(path)
    start = getcwd() if start is None else fsdecode(start)
    if splitdrive(path)[0].lower() != splitdrive(start)[0].lower():
        # Path on different drive
        return path

    return _relpath(path, start)


def run(*args, **kwargs) -> CompletedProcess[Any]:
    """Run command with arguments."""
    proc: CompletedProcess[Any] = _run(*args, capture_output=True, **kwargs)
    if proc.returncode:
        raise OSError(proc.stderr.decode().strip())

    return proc


def use_main_dir() -> None:
    """Use the directory of the main script as working directory."""
    chdir(dirname(executable) if getattr(sys, "frozen", False) else syspath[0])
