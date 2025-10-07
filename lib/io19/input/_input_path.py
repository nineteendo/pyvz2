"""19.io class & function for dealing with path input & configs."""
# TODO - Support aliases
# TODO - Implement chown & mknod
# TODO - Remove change checker, will be replaced by separate draw thread

# Linting arguments
# mypy: disable-error-code=misc
# pylint: disable=useless-suppression
# ...
# pylint: disable=too-many-locals, too-many-boolean-expressions
# pylint: disable=too-many-instance-attributes, too-many-branches
# pylint: disable=too-many-return-statements, too-many-statements

# Standard libraries
from errno import EEXIST, ENOTDIR
from logging import exception
from os import (
    chmod, curdir, fsdecode, makedirs, mkdir, pardir, readlink, rename, sep,
    stat, supports_follow_symlinks, symlink, unlink
)
from os.path import (
    abspath, basename, dirname, exists, expanduser, isdir, isfile, islink,
    join, splitext,
)
from pathlib import Path
from shutil import SameFileError, copy, copytree, move, rmtree
from threading import Thread
from typing import Any, NoReturn, Optional, Union

# Custom libraries
from ...sortext import natsort, natsorted
from ..output.ansi import erase_in_line
from ..output.colors import cyan, dim, green, light_blue, red, yellow
from ..path import (
    DEFROOT, StrOrBytesPath, commonpath, edit, isexecutable, isfifo, ishidden,
    isjunction, isroot, issocket, isvalid, iswhiteout, junction, link, mkfifo,
    move2trash, process_path, relpath, listdir
)
from ..translate import gettext as _
from ._classes import Exit, Info, Representation
from ._input_bytes import input_str
from ._input_enum import (
    BaseDictPicker, BaseSequencePicker, category, dict_picker,
)
from ._input_event import input_event
from .keyboard import is_printable

__all__: list[str] = ['ConfigPicker', 'Extensions', 'InputPath', 'Prefixes']
__all__ += ['config_picker', 'input_path']
_MAX_NAME_LENGTH: int = 255
_MAX_PATH_LENGTH: int = 4096

Extensions = Union[str, tuple[str, ...]]
Prefixes = Union[str, tuple[str, ...]]


class ConfigPicker(BaseDictPicker[str, NoReturn, str, Info, Path]):
    """Class for config pickers."""

    def __init__(  # noqa: MC0001
        self, title: Any, cwd: StrOrBytesPath, field: int, *,
        category_extensions: Extensions = '.txt', clear: bool = False,
        config_extensions: Extensions = '.json', confirm: bool = False,
        dirs_only: bool = False, fields: int = 2, files_only: bool = False,
        hidden_prefixes: Prefixes = ('.', '$', '~$'),
        make_lowercase: bool = False, make_uppercase: bool = False,
        placeholder: Optional[str] = None,
        representation: type[str] = Representation,
        show_hidden_items: bool = False
    ) -> None:
        """Make new ConfigPicker instance."""
        if isinstance(category_extensions, str):
            category_extensions = (category_extensions,)

        cwd = abspath(expanduser(fsdecode(cwd)))
        if isinstance(config_extensions, str):
            config_extensions = (config_extensions,)

        if isinstance(hidden_prefixes, str):
            hidden_prefixes = (hidden_prefixes,)

        if category_extensions and not config_extensions or not all(
            config_extension not in category_extensions
            for config_extension in config_extensions
        ):
            raise ValueError(
                "category_extensions & config_extensions can't overlap"
            )

        if not all(
            all(map(is_printable, category_extension))
            for category_extension in category_extensions
        ):
            raise ValueError('Not all category_extensions are printable')

        if not all(
            all(map(is_printable, config_extension))
            for config_extension in config_extensions
        ):
            raise ValueError('Not all config_extensions are printable')

        if not isdir(cwd):
            raise NotADirectoryError(ENOTDIR, 'Not a directory', cwd)

        if dirs_only and files_only:
            raise ValueError('dirs_only & files_only are mutually exclusive')

        if not 0 <= field < fields:
            raise ValueError('field must lay between 0 & fields')

        options: dict[str, Union[Info, str]] = {}
        for item in natsorted(listdir(cwd)):
            name: str
            path: str = join(cwd, item)
            extension: str
            name, extension = splitext(item)
            if (
                # Hide broken symlinks
                not exists(path) or
                # Check file
                isfile(path) and (
                    dirs_only or
                    extension not in category_extensions and
                    config_extensions and extension not in config_extensions
                ) or
                # Hide dirs in files only mode
                isdir(path) and files_only or
                # Hide hidden items
                item.startswith(hidden_prefixes) and not show_hidden_items or
                # Incorrect number of fiels
                name.count('--') != fields
            ):
                continue

            key: str
            key, _1, name = name.partition('--')
            if (
                isdir(path) or not config_extensions or
                extension in config_extensions
            ):
                options[key] = name + extension
            else:
                options[key] = Info(name + extension)

        self.cwd: str = cwd
        self.field: int = field
        super().__init__(
            title, options, clear=clear, confirm=confirm,
            make_lowercase=make_lowercase, make_uppercase=make_uppercase,
            placeholder=placeholder, representation=representation,
            select_key=True
        )

    def print_key_value(
        self, i: int, key: str, value: Union[str, Info]
    ) -> None:
        """Print key value with indicator when selected."""
        option: str = value.value if isinstance(value, Info) else value
        option = splitext(option)[0].split('--')[self.field].replace('_', ' ')
        option += sep if isdir(join(self.cwd, f'{key}--{value}')) else ''
        super().print_key_value(
            i, key, Info(option) if isinstance(value, Info) else option
        )

    def submit_choice(self, option: str) -> tuple[bool, Optional[Path]]:
        """Submit choice."""
        return True, Path(join(self.cwd, f'{option}--{self.options[option]}'))


class InputPath(BaseSequencePicker[str, NoReturn, Path]):
    """Input path."""

    def __init__(  # noqa: MC0001
        self, title: Any, cwd: StrOrBytesPath, *, all_dirs: bool = True,
        allow_chmod: bool = False, allow_copy: bool = False,
        allow_create: bool = False, allow_delete: bool = False,
        allow_link: bool = True, allow_move: bool = False,
        allow_open: bool = False, allow_rename: bool = False,
        clear: bool = False, confirm: bool = False, dirs_only: bool = False,
        files_only: bool = False, file_extensions: Extensions = (),
        hidden_prefixes: Prefixes = ('.', '$', '~$'),
        home: Optional[StrOrBytesPath] = None, make_lowercase: bool = False,
        make_uppercase: bool = False, placeholder: Optional[str] = None,
        representation: type[str] = Representation,
        show_broken_links: bool = True, show_hidden_items: bool = False,
        show_special: bool = False, sub_dirs: bool = True
    ) -> None:
        """Make new InputPath instance."""
        all_dirs = all_dirs and sub_dirs
        allow_create = allow_copy or allow_create
        allow_link = allow_create and allow_link
        allow_move = allow_move or allow_copy and allow_delete
        if (
            allow_chmod or allow_copy or allow_delete or allow_move or
            allow_open or allow_rename
        ):
            # Enable item actions
            confirm = True

        cwd = abspath(expanduser(fsdecode(cwd)))
        value: str = ''
        if not isdir(cwd):
            # Set cwd to first existing parent directory, user input to rest
            if isroot(cwd):
                cwd, value = DEFROOT, cwd
            else:
                cwd, value = dirname(cwd), basename(cwd)

            while not isdir(cwd):
                if isroot(cwd):
                    cwd, value = DEFROOT, join(cwd, value)
                else:
                    cwd, value = dirname(cwd), join(basename(cwd), value)

        value = repr(value) if value else value
        if dirs_only and files_only:
            raise ValueError('dirs_only & files_only are mutually exclusive')

        if isinstance(file_extensions, str):
            file_extensions = (file_extensions,)

        if not all(
            all(map(is_printable, file_extension))
            for file_extension in file_extensions
        ):
            raise ValueError('Not all file_extensions are printable')

        if isinstance(hidden_prefixes, str):
            hidden_prefixes = (hidden_prefixes,)

        home = cwd if home is None else abspath(expanduser(fsdecode(home)))
        if not isdir(home):
            raise NotADirectoryError(ENOTDIR, 'Not a directory', home)

        if not all_dirs and commonpath([home, cwd]) != home:
            raise ValueError('cwd must be a subdir of home')

        show_special = show_special and not dirs_only and not files_only
        if not sub_dirs and cwd != home:
            raise ValueError('cwd must be home')

        self.all_dirs: bool = all_dirs
        self.allow_chmod: bool = allow_chmod
        self.allow_copy: bool = allow_copy
        self.allow_create: bool = allow_create
        self.allow_delete: bool = allow_delete
        self.allow_link: bool = allow_link
        self.allow_move: bool = allow_move
        self.allow_open: bool = allow_open
        self.allow_rename: bool = allow_rename
        self.checking: bool = False
        self.cwd: str = cwd
        self.dirs_only: bool = dirs_only
        self.files_only: bool = files_only
        self.file_extensions: tuple[str, ...] = file_extensions
        self.hidden_prefixes: tuple[str, ...] = hidden_prefixes
        self.home: str = home
        self.show_broken_links: bool = show_broken_links
        self.show_hidden_items: bool = show_hidden_items
        self.show_special: bool = show_special
        self.sub_dirs: bool = sub_dirs
        self.thread: Optional[Thread] = None
        self.vwd: str = cwd
        super().__init__(
            title, [], clear=clear, confirm=confirm,
            make_lowercase=make_lowercase, make_uppercase=make_uppercase,
            max_length=_MAX_PATH_LENGTH, placeholder=placeholder,
            representation=representation, user_input=value
        )

    def get_title(self) -> str:
        """Get title."""
        return f'{self.title} {self.cwd}'

    def update_options(self) -> int:  # noqa: MC0001
        """Get options."""
        while not exists(self.cwd):
            if isroot(self.cwd):
                self.cwd = DEFROOT
            else:
                self.cwd = dirname(self.cwd)

        processed_path: str = process_path(expanduser(self.user_input))
        self.filtered_options.clear()
        self.options.clear()
        vwd: str = abspath(join(self.cwd, dirname(processed_path)))
        if (
            not isvalid(vwd) or
            exists(vwd) and not isdir(vwd) or
            not self.all_dirs and commonpath([self.home, vwd]) != self.home or
            not self.sub_dirs and vwd != self.home
        ):
            self.vwd = self.cwd
            return 0

        self.vwd = vwd
        processed_path = basename(processed_path)
        try:
            # noinspection PyTypeChecker
            if isdir(self.vwd):
                self.options = listdir(self.vwd)
        except OSError:
            if self.screen_height > 3:
                self.screen_height -= 1  # Virtually decrease screen height
                self.cursor_position.next_row()
                if not isexecutable(self.vwd):
                    print(red('>>'), 'Permission denied.', end='')
                else:
                    print(yellow('>>'), _(
                        "Can't list directory items, enter exact item name."
                    ), end='')

                erase_in_line()
                print('\n', end='')

        if (
            processed_path and processed_path not in self.options and
            not islink(join(self.vwd, processed_path)) and
            not isjunction(join(self.vwd, processed_path)) and
            isvalid(join(self.vwd, processed_path))
        ):
            # User input not in options
            self.options.append(processed_path)

        natsort(self.options)
        if (
            (self.all_dirs or self.vwd != self.home) and exists(self.vwd) and
            not isroot(self.vwd)
        ):
            # Allow navigating to parent directory
            self.options = [pardir] + self.options

        self.options = [curdir] + self.options
        for value in self.options:
            path = abspath(join(
                self.vwd, value if self.vwd == self.cwd else value
            ))
            if not (
                # Check filter
                not self.representation(value.lower()).startswith(
                    processed_path.lower()
                ) or
                # Check file type
                not self.show_special and exists(path) and not (
                    isdir(path) or isfile(path)
                ) or
                # Check broken link or new item
                not self.exists(value) and (
                    not self.show_broken_links
                    if islink(path) or isjunction(path) else
                    not self.allow_create or
                    self.files_only and not self.sub_dirs and
                    self.file_extensions and
                    splitext(path)[1] not in self.file_extensions
                ) or
                # Check file
                isfile(path) and (
                    self.dirs_only or
                    self.file_extensions and
                    not splitext(path)[1] in self.file_extensions
                ) or
                # Check dir
                self.files_only and not self.sub_dirs and value != curdir and
                isdir(path) or
                # Check hidden
                not self.show_hidden_items and self.ishidden(value)
            ):
                self.filtered_options.append(value)

        return len(self.filtered_options)

    def exists(self, option: str) -> bool:
        """Return whether the path exists."""
        path: str = abspath(join(
            self.vwd, option if self.vwd == self.cwd else option
        ))
        return (
            option in [curdir, pardir] and self.vwd == self.cwd
        ) or exists(path)

    def ishidden(self, option: str) -> bool:
        """Return whether the path is hidden."""
        path: str = abspath(join(
            self.vwd, option if self.vwd == self.cwd else option
        ))
        return option not in [curdir, pardir] and (
            ishidden(path) or basename(path).startswith(self.hidden_prefixes)
        )

    def print_value(self, i: int, value: str) -> None:  # noqa: MC0001
        """Print option with indicator when selected."""
        vwd_path: str
        if self.vwd == self.cwd:
            vwd_path = ''
        elif commonpath([self.vwd, self.cwd]) == self.cwd:
            vwd_path = relpath(self.vwd, self.cwd)
        else:
            vwd_path = self.vwd

        path: str = abspath(join(self.vwd, value))
        display_option: str = join(vwd_path, value)
        if display_option.startswith('~'):
            display_option = repr(display_option)

        # ls -F characters:
        if value in [curdir, pardir]:
            pass
        elif isdir(path):
            # Dir
            display_option += '' if display_option.endswith(sep) else sep
        elif issocket(path):
            display_option += '='
        elif iswhiteout(path):
            display_option += '%'
        elif isfifo(path):
            display_option += '|'
        elif isexecutable(path):
            display_option += '*'
        elif islink(path):
            display_option += '@'

        display_option = self.representation(display_option)
        display_option = display_option[:max(0, self.screen_width - 2)]
        self.cursor_position.next_row()
        if i != self.scroll_index + self.selected_index:
            if self.exists(value) and not self.ishidden(value):
                # Not selected visible item
                print(end=f'  {display_option}')
            else:
                # Not selected hidden item
                print(end=dim(f'  {display_option}'))
        elif value == curdir and self.vwd == self.cwd and (
            self.files_only or path == self.home and not self.all_dirs
        ):
            # Selected exit (current directory)
            print(end=yellow(f'< {display_option}'))
        elif self.exists(value):
            if islink(path) or isjunction(path):
                # Selected symlink
                print(end=light_blue(f'->{display_option}'))
            else:
                # Selected real item
                print(end=cyan(f'> {display_option}'))
        elif not (islink(path) or isjunction(path)):
            # Selected new item
            print(end=green(f'+ {display_option}'))
        elif self.allow_delete:
            # Selected broken symlink
            print(end=red(f'- {display_option}'))
        else:
            # Selected exit (broken symlink)
            print(end=yellow(f'<-{display_option}'))

        erase_in_line()
        print('\n', end='')

    def confirm_choice(self, option: str) -> bool:  # noqa: MC0001
        """Confirm choice (item actions)."""
        path: str = abspath(join(
            self.vwd, option if self.vwd == self.cwd else option
        ))
        if (
            option == pardir or
            isdir(path) and (option != curdir or self.vwd != self.cwd) and
            self.sub_dirs or
            not self.exists(option) and not (islink(path) or isjunction(path))
        ):
            # No item action
            return True

        self.cleanup()  # Disable thread while in sub menu
        not_home: bool = self.all_dirs or path != self.home
        allow_link: bool = self.allow_delete and self.allow_link
        allow_open: bool = self.allow_open and self.exists(option) and (
            isdir(path) or isfile(path)
        )
        action: Optional[str] = dict_picker(_('Edit {0}').format(path), {
            0:     Exit(_('Cancel')),
            **(category('') if (
                # No file actions
                self.allow_chmod or
                self.allow_copy or
                not_home and (
                    self.allow_delete or self.allow_move or self.allow_rename
                ) or allow_open or
                allow_link and (islink(path) or isjunction(path))
            ) else {}),
            **({
                1: _('Open in default program')
            } if allow_open else {}),
            **({2: _('Copy')} if self.allow_copy else {}),
            **({3: _('Chmod')} if self.allow_chmod else {}),
            **({
                4: _('Edit symlink'),
                5: _('Edit relative symlink')
            } if islink(path) and allow_link else {}),
            **({4: _('Edit junction')} if (
                isjunction(path) and allow_link
            ) else {}),
            **({6: _('Rename')} if self.allow_rename and not_home else {}),
            **({7: _('Move')} if self.allow_move and not_home else {}),
            **({8: _('Delete')} if self.allow_delete and not_home else {}),
            **category(''),
            9:     Exit(_('Exit')) if (
                not exists(path) or option == curdir and
                self.vwd == self.cwd and (
                    self.files_only or path == self.home and not self.all_dirs
                )
            ) else _('Submit')
        }, clear=True, representation=self.representation)
        if action is None or action == Exit(_('Cancel')):
            return False

        if action in [_('Submit'), Exit(_('Exit'))]:
            return True

        try:
            if action == _('Open in default program'):
                edit(path)
            elif action in [_('Copy'), _('Move')]:
                dst: Optional[Path] = input_path(
                    _('Select destination'), dirname(path),
                    allow_create=self.allow_create, allow_link=False,
                    clear=True, dirs_only=True,
                    hidden_prefixes=self.hidden_prefixes,
                    make_lowercase=self.make_lowercase,
                    make_uppercase=self.make_uppercase,
                    placeholder=self.placeholder,
                    representation=self.representation,
                    show_broken_links=self.show_broken_links,
                    show_hidden_items=self.show_hidden_items
                )
                if dst is None:
                    return False

                dst = Path(abspath(join(dst, basename(path))))
                if exists(dst) and dst != path:
                    confirm: Optional[str] = dict_picker(
                        _('Confirm {0}').format(action), {
                            0:     _('Cancel'),
                            1:     _('Rename'),
                            **({2: _('Replace')} if self.allow_delete else {})
                        }, clear=True, representation=self.representation
                    )
                    if confirm is None or confirm == _('Cancel'):
                        return False

                    if confirm == _('Rename'):
                        pass
                    elif isfile(path) or islink(path) or isjunction(path):
                        unlink(path)
                    elif isdir(path):
                        rmtree(path)

                base_name: str
                counter: int = 1
                extension: str
                base_name, extension = splitext(dst)
                while exists(dst) and (action == _('Copy') or dst != path):
                    dst = Path(f'{base_name} ({counter}){extension}')
                    counter += 1

                if isfile(path) or islink(path) or isjunction(path):
                    if action == _('Move'):
                        move(path, dst)
                    elif action == _('Copy'):
                        copy(path, dst)
                elif action == _('Move'):
                    move(path, dst)
                    if option == curdir:
                        self.cwd = fsdecode(dst)
                elif action == _('Copy'):
                    copytree(path, dst)
            elif action == _('Chmod'):
                follow_symlinks: bool = chmod not in supports_follow_symlinks
                mod: int = stat(path, follow_symlinks=follow_symlinks).st_mode
                name: str
                new_mode: int = 0
                permissions: int
                special_mode: int = 0
                for name, permissions in {
                    _('Owner '): ((mod & 0o4000) >> 8) + ((mod & 0o0700) >> 6),
                    _('Group '): ((mod & 0o2000) >> 7) + ((mod & 0o0070) >> 3),
                    _('Others'): ((mod & 0o1000) >> 6) + ((mod & 0o0007) >> 0)
                }.items():
                    # noinspection PyArgumentEqualDefault
                    permission_string: Optional[str] = dict_picker(
                        _('{0} permissions').format(name), {
                            '00': '---',
                            '01': '--x',
                            '02': '-w-',
                            '03': '-wx',
                            '04': 'r--',
                            '05': 'r-x',
                            '06': 'rw-',
                            '07': 'rwx',
                            '08': '--T' if name == _('Others') else '--S',
                            '09': '--t' if name == _('Others') else '--s',
                            '10': '-wT' if name == _('Others') else '-wS',
                            '11': '-wt' if name == _('Others') else '-ws',
                            '12': 'r-T' if name == _('Others') else 'r-S',
                            '13': 'r-t' if name == _('Others') else 'r-s',
                            '14': 'rwT' if name == _('Others') else 'rwS',
                            '15': 'rwt' if name == _('Others') else 'rws'
                        }, clear=True, key=f'{permissions:02d}',
                        representation=self.representation, select_key=True
                    )
                    if permission_string is None:
                        break

                    new_permissions: int = int(permission_string)
                    new_mode <<= 3
                    new_mode += new_permissions & 0o7
                    special_mode <<= 1
                    special_mode += (new_permissions & 0o10) >> 3
                else:
                    chmod(
                        path, (special_mode << 9) + new_mode,
                        follow_symlinks=follow_symlinks
                    )
            elif action in [
                _('Edit symlink'), _('Edit relative symlink'),
                _('Edit junction')
            ]:
                src: Optional[Path] = input_path(
                    _('Select new source'), join(
                        dirname(path), readlink(path)
                    ), allow_create=True, allow_link=False, clear=True,
                    dirs_only=isdir(path) or isjunction(path),
                    files_only=isfile(path),
                    file_extensions=self.file_extensions,
                    hidden_prefixes=self.hidden_prefixes,
                    make_lowercase=self.make_lowercase,
                    make_uppercase=self.make_uppercase,
                    placeholder=self.placeholder,
                    representation=self.representation,
                    show_broken_links=self.show_broken_links,
                    show_hidden_items=self.show_hidden_items,
                    show_special=self.show_special
                )
                if src is None or src == path:
                    return False

                unlink(path)
                if action == _('Edit symlink'):
                    symlink(src, path)
                elif action == _('Edit relative symlink'):
                    symlink(relpath(src, dirname(path)), path)
                elif action == _('Edit junction'):
                    junction(src, path)
            elif action == _('Rename'):
                old_name: str = basename(path)
                new_name: Optional[str] = input_str(
                    _('Choose new name:'), clear=True,
                    make_lowercase=self.make_lowercase,
                    make_uppercase=self.make_uppercase,
                    max_length=_MAX_NAME_LENGTH, value=old_name
                )
                if not new_name or new_name is None:
                    return False

                newpath: str = abspath(join(dirname(path), new_name))
                if new_name == old_name or dirname(newpath) != dirname(path):
                    return False

                if exists(newpath) or islink(newpath) or isjunction(newpath):
                    raise FileExistsError(EEXIST, 'File exists', newpath)

                rename(path, newpath)
                if option == curdir:
                    # Renamed cwd
                    self.cwd = newpath
            elif action == _('Delete'):
                if move2trash(path):
                    return False

                if dict_picker(
                    _('Confirm {0}').format(action), {
                        0: Exit(_('Cancel')),
                        1: _('Delete')
                    }, clear=True, representation=self.representation
                ) != _('Delete'):
                    return False

                if isfile(path) or islink(path) or isjunction(path):
                    unlink(path)
                elif isdir(path):
                    rmtree(path)
        except (
            FileExistsError, OSError, PermissionError, SameFileError
        ) as err:
            exception(err)
            input_event(err, clear=True)

        return False

    def submit_choice(  # noqa: MC0001
        self, _1: str
    ) -> tuple[bool, Optional[Path]]:
        """Submit choice."""
        selectable: bool
        option: Union[Info, str]
        selectable, option = self.get_selected_option()
        if not selectable or isinstance(option, Info):
            raise RuntimeError('Option is not selectable')

        path: str = abspath(join(
            self.vwd, option if self.vwd == self.cwd else option
        ))
        if option == curdir and self.vwd == self.cwd and (
            self.files_only or path == self.home and not self.all_dirs
        ) or not self.exists(option) and (islink(path) or isjunction(path)):
            # Exit
            return True, None

        if (
            isfifo(path) or isfile(path) or
            option == curdir and self.vwd == self.cwd or
            isdir(path) and not self.sub_dirs
        ):
            # Submit
            return True, Path(path)

        if isdir(path) or option == pardir:
            # Change directory
            self.cwd = path
            self.scroll_index = self.selected_index = 0
            self.user_input = ''
            return False, Path(path)

        self.cleanup()  # Disable thread while in sub menu
        allow_mkdir: bool = not self.files_only or self.sub_dirs
        create: Optional[str] = dict_picker(
            _('Create {0}').format(path), {
                0:     Exit(_('Cancel')),
                **category(''),
                **({1: _('File')} if (
                    not self.file_extensions or
                    not self.dirs_only and
                    splitext(path)[1] in self.file_extensions
                ) else {}),
                **({2: _('Dir')} if allow_mkdir else {}),
                **({3: _('Link')} if (
                    not self.dirs_only and self.allow_link and (
                        splitext(path)[1] in self.file_extensions or
                        not self.file_extensions
                    )
                ) else {}),
                **({
                    4: _('Symlink'),
                    5: _('Relative symlink')
                } if self.allow_link else {}),
                **({6: _('Junction')} if (
                    allow_mkdir and self.allow_link
                ) else {}),
                **({7: _('Fifo')} if self.show_special else {})
            }, clear=True, make_lowercase=self.make_lowercase,
            make_uppercase=self.make_uppercase,
            representation=self.representation
        )
        if create is None or isinstance(create, Exit):
            return False, Path(path)

        try:
            makedirs(dirname(path), exist_ok=True)
            if create == _('File'):
                with open(path, 'wb'):
                    pass
            elif create == _('Dir'):
                mkdir(path)
            elif create in [
                _('Link'), _('Symlink'), _('Relative symlink'), _('Junction')
            ]:
                src: Optional[Path] = input_path(
                    _('Select source'), self.cwd, allow_create=True,
                    allow_link=False, clear=True,
                    dirs_only=self.dirs_only or create == _('Junction'),
                    files_only=self.files_only or create == _('Link'),
                    file_extensions=self.file_extensions,
                    hidden_prefixes=self.hidden_prefixes,
                    make_lowercase=self.make_lowercase,
                    make_uppercase=self.make_uppercase,
                    placeholder=self.placeholder,
                    representation=self.representation,
                    show_broken_links=self.show_broken_links,
                    show_hidden_items=self.show_hidden_items,
                    show_special=self.show_special
                )
                if src is None:
                    return False, Path(path)

                if create == _('Link'):
                    link(src, path)
                elif create == _('Symlink'):
                    symlink(src, path)
                elif create == _('Relative symlink'):
                    symlink(relpath(src, dirname(path)), path)
                elif create == _('Junction'):
                    junction(src, path)
            elif create == _('Fifo'):
                mkfifo(path)
        except (FileExistsError, OSError, PermissionError) as err:
            exception(err)
            input_event(err, clear=True)

        return False, Path(path)

    def cleanup(self) -> None:
        """Clean up threads."""
        self.checking = False


def config_picker(
    title: Any, cwd: StrOrBytesPath, field: int, *,
    category_extensions: Extensions = '.txt', clear: bool = False,
    config_extensions: Extensions = '.json', confirm: bool = False,
    dirs_only: bool = False, fields: int = 2, files_only: bool = False,
    hidden_prefixes: Prefixes = ('.', '$', '~$'), make_lowercase: bool = False,
    make_uppercase: bool = False, placeholder: Optional[str] = None,
    representation: type[str] = Representation, show_hidden_items: bool = False
) -> Optional[Path]:
    """Config picker using ConfigPicker."""
    return ConfigPicker(
        title, cwd, field, category_extensions=category_extensions,
        clear=clear, config_extensions=config_extensions,
        confirm=confirm,
        dirs_only=dirs_only, fields=fields, files_only=files_only,
        hidden_prefixes=hidden_prefixes, make_lowercase=make_lowercase,
        make_uppercase=make_uppercase, placeholder=placeholder,
        representation=representation, show_hidden_items=show_hidden_items
    ).get_value()


def input_path(
    title: Any, cwd: StrOrBytesPath, *, all_dirs: bool = True,
    allow_chmod: bool = False, allow_copy: bool = False,
    allow_create: bool = False, allow_delete: bool = False,
    allow_link: bool = True, allow_move: bool = False,
    allow_open: bool = False, allow_rename: bool = False, clear: bool = False,
    dirs_only: bool = False, files_only: bool = False,
    file_extensions: Extensions = (),
    hidden_prefixes: Prefixes = ('.', '$', '~$'),
    home: Optional[StrOrBytesPath] = None, make_lowercase: bool = False,
    make_uppercase: bool = False, placeholder: Optional[str] = None,
    representation: type[str] = Representation, show_broken_links: bool = True,
    show_hidden_items: bool = False, sub_dirs: bool = True,
    show_special: bool = False
) -> Optional[Path]:
    """Read path from console input."""
    return InputPath(
        title, cwd, all_dirs=all_dirs, allow_chmod=allow_chmod,
        allow_copy=allow_copy, allow_create=allow_create,
        allow_delete=allow_delete, allow_link=allow_link,
        allow_move=allow_move, allow_open=allow_open,
        allow_rename=allow_rename, clear=clear, dirs_only=dirs_only,
        files_only=files_only, file_extensions=file_extensions,
        hidden_prefixes=hidden_prefixes, home=home,
        make_lowercase=make_lowercase, make_uppercase=make_uppercase,
        placeholder=placeholder, representation=representation,
        show_broken_links=show_broken_links,
        show_hidden_items=show_hidden_items, show_special=show_special,
        sub_dirs=sub_dirs
    ).get_value()
