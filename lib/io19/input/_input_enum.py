"""19.io classes & functions for dict, list pickers & enum input."""
# TODO - Separate thread to display text
# TODO - Handle height of 1 -> new key handler
# TODO - Keep selected option when filtering
# TODO - Make function for moving & scrolling -> select first selectable
# TODO - Smart cut off

# Linting arguments
# pylint: disable=too-many-branches, too-many-locals, too-many-statements

# Standard libraries
from abc import ABCMeta, abstractmethod
from cmath import inf
from collections.abc import Sequence
from typing import Any, Generic, Literal, Optional, Union, overload

# Custom libraries
from ..output.ansi import erase_in_line
from ..output.colors import cyan, dim, red, yellow
from ..real2float import Real
from ..translate import gettext as _
from ._classes import (ENUM, KEY, KEYINFO, RESULT, VALUE, VALUEINFO, Exit,
                       Info, Representation, Unique)
from ._input_bytes import BaseInputStr
from .keyboard import CtrlCodes, CtrlSequences, Event, MouseButtons, RawInput

__all__: list[str] = [
    'BaseDictPicker', 'BasePicker', 'BaseSequencePicker', 'DictPicker',
    'SequencePicker'
]
__all__ += [
    'category', 'dict_picker', 'entities', 'identity', 'input_enum',
    'sequence_picker'
]


def identity(key: KEY) -> dict[KEY, KEY]:
    """Return dict with identity mapping."""
    return {key: key}


def entities(*keys: KEY) -> dict[Unique[KEY], Unique[KEY]]:
    """Return dict with identity unique mapping."""
    return {key: key for key in map(Unique[KEY], keys)}


def category(key: KEY) -> dict[Info[KEY], Info[KEY]]:
    """Return dict with identity info mapping."""
    return identity(Info(key))


class BasePicker(
    BaseInputStr[RESULT], Generic[KEY, KEYINFO, VALUE, VALUEINFO, RESULT]
):
    """Base Picker."""

    @abstractmethod
    def __init__(
        self, title: Any, *, clear: bool = False, confirm: bool = False,
        make_lowercase: bool = False, make_uppercase: bool = False,
        max_length: Real = inf, placeholder: Optional[str] = None,
        representation: type[str] = Representation,
        select_key: bool = False, selected_index: int = 0,
        user_input: Optional[str] = None
    ) -> None:
        """Make new BasePicker instance."""
        self.confirm: bool = confirm
        self.length: int = 0
        self.screen_height: int = 0
        self.scroll_index: int = 0
        self.select_key: bool = select_key
        self.selected_index: int = selected_index
        super().__init__(
            title, clear=clear, make_lowercase=make_lowercase,
            make_uppercase=make_uppercase, max_length=max_length,
            placeholder=(
                _('Use arrow keys') if placeholder is None else placeholder
            ), representation=representation, value=user_input
        )

    @abstractmethod
    def update_options(self) -> int:
        """Get options."""

    def is_visible(self, i: int) -> bool:
        """Return if the current option is visible."""
        return 3 <= i + 3 - self.scroll_index <= self.screen_height

    @abstractmethod
    def display_options(self) -> None:
        """Display options."""

    @abstractmethod
    def get_selected_option(self, select_key: bool = False) -> tuple[
        bool, Union[KEY, KEYINFO, VALUE, VALUEINFO]
    ]:
        """Get currently selected option."""

    def display_info(self) -> None:
        """Display additional info beside the title."""
        if self.screen_height == 2:
            self.cursor_position.move_back(self.cursor_position.chars)
            print('\r', end='')
            self.screen_height += 1  # Virtually increase screen height
        else:
            self.cursor_position.next_row()
            erase_in_line()
            print('\n', end='')

        self.length = self.update_options()
        message: str
        if self.length:
            pass
        elif self.user_input:
            message = _('No items match your search, clear filter.')
            self.cursor_position += 3 + len(message)
            self.cursor_position.next_row()
            print(yellow('>>'), message, end='')
            erase_in_line()
            print('\n', end='')
            return None
        else:
            message = _('No selectable items, press enter.')
            self.cursor_position += 3 + len(message)
            self.cursor_position.next_row()
            print(red('>>'), message, end='')
            erase_in_line()
            print('\n', end='')
            return None

        if self.scroll_index + self.selected_index >= self.length:
            # Index out of bounds -> select last option
            self.scroll_index = max(0, self.length + 2 - self.screen_height)
            self.selected_index = min(self.screen_height - 3, self.length - 1)
        elif self.scroll_index and (
            self.scroll_index + self.screen_height > self.length + 2
        ):
            # Scrolled too far down -> scroll up
            scroll_up: int = self.scroll_index - max(
                0, self.length + 2 - self.screen_height
            )
            self.scroll_index -= scroll_up
            self.selected_index += scroll_up
        elif self.selected_index + 2 >= self.screen_height:
            # Off screen -> scroll down
            scroll_down: int = self.selected_index + 3 - self.screen_height
            self.scroll_index += scroll_down
            self.selected_index -= scroll_down

        if not self.get_selected_option()[0]:
            # Select first selectable option
            self.handle_user_input(Event(special=CtrlSequences.DOWN))

        return self.display_options()

    def handle_user_input(self, event: Event) -> bool:  # noqa: MC0001
        """Handle user input."""
        if event.special in [
            CtrlSequences.UP, CtrlSequences.SHIFT_TAB
        ] and self.length > 1:
            # Select previous option
            for _1 in range(self.length):  # Saveguard
                if self.selected_index:
                    self.selected_index -= 1
                elif self.scroll_index:
                    self.scroll_index -= 1
                else:
                    self.scroll_index = max(
                        0, self.length + 2 - self.screen_height
                    )
                    self.selected_index = min(
                        self.screen_height - 3, self.length - 1
                    )

                if self.get_selected_option()[0]:
                    break
        elif event.button_down == MouseButtons.B and self.length > 1:
            # Scroll options one up
            for _1 in range(self.length):  # Saveguard
                if self.scroll_index:
                    self.scroll_index -= 1
                elif self.selected_index:
                    self.selected_index -= 1
                else:
                    self.scroll_index = max(
                        0, self.length + 2 - self.screen_height
                    )
                    self.selected_index = min(
                        self.screen_height - 3, self.length - 1
                    )

                if self.get_selected_option()[0]:
                    break
        elif event.button_down == MouseButtons.META_B and (
            self.length > 1 and self.length + 2 >= self.screen_height
        ):
            # Go to previous options page
            if not self.scroll_index:
                self.scroll_index = self.length + 2 - self.screen_height
            elif self.scroll_index + 2 <= self.screen_height:
                self.scroll_index = 0
            else:
                self.scroll_index -= self.screen_height - 2

            for _1 in range(self.length):  # Saveguard
                if self.get_selected_option()[0]:
                    break

                if self.scroll_index:
                    self.scroll_index -= 1
                elif self.selected_index:
                    self.selected_index -= 1
                else:
                    self.scroll_index = self.length + 2 - self.screen_height
                    self.selected_index = self.screen_height - 3
        elif event.special in [
            CtrlCodes.HORIZONTAL_TABULATION, CtrlSequences.DOWN
        ] and self.length > 1:
            # Select next option
            for _1 in range(self.length):  # Saveguard
                if self.scroll_index + self.selected_index + 1 == self.length:
                    self.scroll_index = self.selected_index = 0
                elif self.selected_index + 3 < self.screen_height:
                    self.selected_index += 1
                else:
                    self.scroll_index += 1

                if self.get_selected_option()[0]:
                    break
        elif event.button_down == MouseButtons.F and self.length > 1:
            # Scroll options one down
            for _1 in range(self.length):  # Saveguard
                if self.scroll_index + self.selected_index + 1 == self.length:
                    self.scroll_index = self.selected_index = 0
                elif self.scroll_index + self.screen_height < self.length + 2:
                    self.scroll_index += 1
                else:
                    self.selected_index += 1

                if self.get_selected_option()[0]:
                    break
        elif event.button_down == MouseButtons.META_F and (
            self.length > 1 and self.length + 2 >= self.screen_height
        ):
            # Go to next options page
            if self.scroll_index == self.length - self.screen_height + 2:
                self.scroll_index = 0
            elif self.scroll_index + 2 * self.screen_height > self.length + 4:
                self.scroll_index = self.length - self.screen_height + 2
            else:
                self.scroll_index += self.screen_height - 2

            for _1 in range(self.length):  # Saveguard
                if self.get_selected_option()[0]:
                    break

                if self.scroll_index + self.selected_index + 1 == self.length:
                    self.scroll_index = self.selected_index = 0
                elif self.scroll_index + self.screen_height < self.length + 2:
                    self.scroll_index += 1
                else:
                    self.selected_index += 1
        else:
            user_input: str = self.user_input
            result: bool = super().handle_user_input(event)
            if self.user_input != user_input:
                self.scroll_index = self.selected_index = 0

            return result

        return True

    def confirm_choice(self, option: Union[KEY, VALUE]) -> bool:
        """Confirm choice."""
        return dict_picker(_('Confirm {0}').format(option), {
            0: _('No'),
            1: _('Yes')
        }, clear=True, representation=self.representation) == _('Yes')

    @abstractmethod
    def submit_choice(self, option: Union[KEY, VALUE]) -> tuple[
        bool, Optional[RESULT]
    ]:
        """Submit choice."""

    def submit(self) -> tuple[bool, Optional[RESULT]]:
        """Submit value as result."""
        if self.length:
            pass
        elif self.user_input:
            # Filter not cleared
            return False, None
        else:
            # Exit
            return True, None

        selectable: bool
        option: Union[KEY, KEYINFO, VALUE, VALUEINFO]
        selectable, option = self.get_selected_option(self.select_key)
        if not selectable or isinstance(option, Info):
            raise RuntimeError('Option is not selectable')

        if self.confirm and not self.confirm_choice(option):
            RawInput.enable()
            return False, None

        confirmed: bool
        result: Optional[RESULT]
        confirmed, result = self.submit_choice(option)
        if not confirmed:
            RawInput.enable()
            return False, None

        return True, result


class BaseDictPicker(
    BasePicker[KEY, KEYINFO, VALUE, VALUEINFO, RESULT], metaclass=ABCMeta
):
    """Base Dict Picker."""

    def __init__(
        self, title: Any,
        options: dict[Union[KEY, KEYINFO], Union[VALUE, VALUEINFO]], *,
        clear: bool = False, confirm: bool = False,
        key: Optional[Union[KEY, KEYINFO]] = None,
        make_lowercase: bool = False, make_uppercase: bool = False,
        max_length: Optional[Real] = None, placeholder: Optional[str] = None,
        representation: type[str] = Representation,
        select_key: bool = False, user_input: Optional[str] = None,
        value: Optional[Union[VALUE, VALUEINFO]] = None
    ) -> None:
        """Make new BaseDictPicker instance."""
        if not (
            key is None and user_input is None or
            key is None and value is None or
            user_input is None and value is None
        ):
            raise ValueError('key, value & user_input are mutually exclusive')

        key_length: int = max((
            len(representation(key)) for key, value in options.items() if
            not isinstance(key, Info) and not isinstance(value, Info)
        ), default=0)
        if max_length is None:
            max_length = key_length
        elif not 0 <= key_length <= max_length <= inf:
            raise ValueError('max_length is smaller than of largest key')

        selected_index: int = 0
        if key is not None:
            selected_index = list(options.keys()).index(key)
        elif value is not None:
            selected_index = list(options.values()).index(value)

        self.filtered_options: dict[
            Union[KEY, KEYINFO], Union[VALUE, VALUEINFO]
        ] = {}
        self.key_width: int = 0
        self.options: dict[
            Union[KEY, KEYINFO], Union[VALUE, VALUEINFO]
        ] = options
        super().__init__(
            title, clear=clear, confirm=confirm, make_lowercase=make_lowercase,
            make_uppercase=make_uppercase, max_length=max_length,
            placeholder=placeholder, representation=representation,
            select_key=select_key, selected_index=selected_index,
            user_input=user_input
        )

    def update_options(self) -> int:
        """Get options."""
        self.filtered_options.clear()
        no_selectable_options: bool = True
        for key, value in self.options.items():
            if not self.representation(key).lower().startswith(
                self.user_input.lower()
            ):
                # Check filter
                continue

            self.filtered_options[key] = value
            if not (isinstance(key, Info) or isinstance(value, Info)):
                no_selectable_options = False

        if no_selectable_options:
            self.filtered_options.clear()

        return len(self.filtered_options)

    def print_key_value(
        self, i: int, key: Union[KEY, KEYINFO], value: Union[VALUE, VALUEINFO]
    ) -> None:
        """Print key value with indicator when selected."""
        option: str
        if key is value:
            option = self.representation(key)
            option = option.rjust(min(
                max(0, self.screen_width - 3),
                self.key_width + len(option) // 2
            ))
            option = option[:self.screen_width - 2]
        else:
            key_option: str = self.representation(key)
            key_option = key_option[:max(0, self.screen_width - 4)].rjust(
                min(max(0, self.screen_width - 4), self.key_width)
            )
            value_option: str = self.representation(value)
            value_option = (
                value_option[:max(0, self.screen_width - len(key_option) - 4)]
            )
            option = f'{key_option}: {value_option}'

        if isinstance(key, Info) or isinstance(value, Info):
            option = dim(option)

        self.cursor_position.next_row()
        if i != self.scroll_index + self.selected_index:
            # Unselected option
            print(end=f'  {option}')
        elif (
            isinstance(key, Exit) or key is None if self.select_key else
            isinstance(value, Exit) or value is None
        ):
            # Exit
            print(end=yellow(f'< {option}'))
        else:
            # Normal option
            print(end=cyan(f'> {option}'))

        erase_in_line()
        print('\n', end='')

    def display_options(self) -> None:
        """Display options."""
        self.key_width = max(
            (len(self.representation(k)) - 2) // 2 if k is v else
            len(self.representation(k))
            for k, v in self.filtered_options.items()
        )
        for i, (key, value) in enumerate(self.filtered_options.items()):
            if self.is_visible(i):
                self.print_key_value(i, key, value)

    def get_selected_option(self, select_key: bool = False) -> tuple[
        bool, Union[KEY, KEYINFO, VALUE, VALUEINFO]
    ]:
        """Get currently selected option."""
        key: Union[KEY, KEYINFO] = list(self.filtered_options.keys())[
            self.scroll_index + self.selected_index
        ]
        value: Union[VALUE, VALUEINFO] = self.options[key]
        return (
            not isinstance(key, Info) and not isinstance(value, Info),
            key if select_key else value
        )


class DictPicker(
    BaseDictPicker[KEY, Info, VALUE, Info, Union[KEY, VALUE]],
    Generic[KEY, VALUE]
):
    """Pick key / value from dict."""

    def submit_choice(self, option: Union[KEY, VALUE]) -> tuple[
        bool, Optional[Union[KEY, VALUE]]
    ]:
        """Submit choice."""
        return True, option


class BaseSequencePicker(
    BasePicker[VALUE, VALUEINFO, VALUE, VALUEINFO, RESULT],
    Generic[VALUE, VALUEINFO, RESULT], metaclass=ABCMeta
):
    """Base Sequence Picker."""

    def __init__(
        self, title: Any, options: Sequence[Union[VALUE, VALUEINFO]], *,
        clear: bool = False, confirm: bool = False,
        index: Optional[int] = None, make_lowercase: bool = False,
        make_uppercase: bool = False, max_length: Optional[Real] = None,
        placeholder: Optional[str] = None,
        representation: type[str] = Representation,
        user_input: Optional[str] = None,
        value: Optional[Union[VALUE, VALUEINFO]] = None
    ) -> None:
        """Make new BaseSequencePicker instance."""
        if not (
            index is None and user_input is None or
            index is None and value is None or
            user_input is None and value is None
        ):
            raise ValueError('key, value & user_input are mutually exclusive')

        options = list(options)
        selected_index: int = 0
        # noinspection PyTypeChecker
        if value is not None:
            selected_index = options.index(value)
        elif index is None:
            pass
        elif not 0 <= index < len(options):
            raise IndexError('list index out of range')
        else:
            # noinspection PyTypeChecker
            selected_index = index

        value_length: int = max((
            len(representation(option))
            for option in options if not isinstance(option, Info)
        ), default=0)
        if max_length is None:
            max_length = value_length
        elif not 0 <= value_length <= max_length <= inf:
            raise ValueError('max_length is smaller than of largest value')

        self.filtered_options: list[Union[VALUE, VALUEINFO]] = []
        self.options: list[Union[VALUE, VALUEINFO]] = options
        super().__init__(
            title, clear=clear, confirm=confirm,
            make_lowercase=make_lowercase, make_uppercase=make_uppercase,
            max_length=max_length, placeholder=placeholder,
            representation=representation, selected_index=selected_index,
            user_input=user_input
        )

    def update_options(self) -> int:
        """Get options."""
        self.filtered_options.clear()
        no_selectable_options: bool = True
        for value in self.options:
            if not self.representation(value).lower().startswith(
                self.user_input.lower()
            ):
                continue

            self.filtered_options.append(value)
            if not isinstance(value, Info):
                no_selectable_options = False

        if no_selectable_options:
            self.filtered_options.clear()

        return len(self.filtered_options)

    def print_value(self, i: int, value: Union[VALUE, VALUEINFO]) -> None:
        """Print option with indicator when selected."""
        option: str = self.representation(value)
        option = option[:max(0, self.screen_width - 2)]
        if isinstance(value, Info):
            option = dim(option)

        self.cursor_position.next_row()
        if i != self.scroll_index + self.selected_index:
            # Unselected option
            print(end=f'  {option}')
        elif isinstance(value, Exit) or value is None:
            # Exit
            print(end=yellow(f'< {option}'))
        else:
            # Normal option
            print(end=cyan(f'> {option}'))

        erase_in_line()
        print('\n', end='')

    def display_options(self) -> None:
        """Display options."""
        for i, value in enumerate(self.filtered_options):
            if self.is_visible(i):
                self.print_value(i, value)

    def get_selected_option(self, _1: bool = False) -> tuple[
        bool, Union[VALUE, VALUEINFO]
    ]:
        """Get currently selected option."""
        value: Union[VALUE, VALUEINFO] = self.filtered_options[
            self.scroll_index + self.selected_index
        ]
        return not isinstance(value, Info), value


class SequencePicker(BaseSequencePicker[VALUE, Info, VALUE], Generic[VALUE]):
    """Pick value from sequence / variable-length arguments."""

    def submit_choice(self, option: VALUE) -> tuple[bool, Optional[VALUE]]:
        """Submit choice."""
        return True, option


@overload
def dict_picker(
    title: Any, options: dict[Union[KEY, Info], Union[VALUE, Info]], *,
    clear: bool = False, confirm: bool = False,
    key: Optional[Union[KEY, Info]] = None,
    make_lowercase: bool = False, make_uppercase: bool = False,
    placeholder: Optional[str] = None,
    representation: type[str] = Representation,
    select_key: Literal[False] = False, user_input: Optional[str] = None,
    value: Optional[Union[VALUE, Info]] = None
) -> Optional[VALUE]:
    """Pick value from dict using console input."""


@overload
def dict_picker(
    title: Any, options: dict[Union[KEY, Info], Union[VALUE, Info]], *,
    clear: bool = False, confirm: bool = False,
    key: Optional[Union[KEY, Info]] = None, make_lowercase: bool = False,
    make_uppercase: bool = False, placeholder: Optional[str] = None,
    representation: type[str] = Representation,
    select_key: Literal[True] = ..., user_input: Optional[str] = None,
    value: Optional[Union[VALUE, Info]] = None
) -> Optional[KEY]:
    """Pick key from dict using console input."""


def dict_picker(
    title: Any, options: dict[Union[KEY, Info], Union[VALUE, Info]], *,
    clear: bool = False, confirm: bool = False,
    key: Optional[Union[KEY, Info]] = None, make_lowercase: bool = False,
    make_uppercase: bool = False, placeholder: Optional[str] = None,
    representation: type[str] = Representation,
    select_key: bool = False, user_input: Optional[str] = None,
    value: Optional[Union[VALUE, Info]] = None
) -> Optional[Union[KEY, VALUE]]:
    """Pick key / value from dict using console input."""
    return DictPicker[KEY, VALUE](
        title, options, clear=clear, confirm=confirm, key=key,
        make_lowercase=make_lowercase, make_uppercase=make_uppercase,
        placeholder=placeholder, representation=representation,
        select_key=select_key, user_input=user_input, value=value
    ).get_value()


@overload
def sequence_picker(
    title: Any, __options: Sequence[Union[VALUE, Info]], *,
    clear: bool = False, confirm: bool = False, index: Optional[int] = None,
    make_lowercase: bool = False, make_uppercase: bool = False,
    placeholder: Optional[str] = None,
    representation: type[str] = Representation,
    user_input: Optional[str] = None,
    value: Optional[Union[VALUE, Info]] = None
) -> Optional[VALUE]:
    """Pick value from sequence using console input."""


@overload
def sequence_picker(
    title: Any, *options: Union[VALUE, Info], clear: bool = False,
    confirm: bool = False, index: Optional[int] = None,
    make_lowercase: bool = False, make_uppercase: bool = False,
    placeholder: Optional[str] = None,
    representation: type[str] = Representation,
    user_input: Optional[str] = None,
    value: Optional[Union[VALUE, Info]] = None
) -> Optional[VALUE]:
    """Pick value from arguments using console input."""


def sequence_picker(
    title: Any, *options: Union[Sequence[Union[VALUE, Info]], VALUE, Info],
    clear: bool = False, confirm: bool = False, index: Optional[int] = None,
    make_lowercase: bool = False, make_uppercase: bool = False,
    placeholder: Optional[str] = None,
    representation: type[str] = Representation,
    user_input: Optional[str] = None,
    value: Optional[Union[Sequence[Union[VALUE, Info]], VALUE, Info]] = None
) -> Optional[Union[Sequence[Union[VALUE, Info]], VALUE]]:
    """Pick value from sequence / arguments using console input."""
    return SequencePicker[Union[Sequence[Union[VALUE, Info]], VALUE]](
        title, options[0] if (
            len(options) == 1 and isinstance(options[0], Sequence)
        ) else options, clear=clear, confirm=confirm, index=index,
        make_lowercase=make_lowercase, make_uppercase=make_uppercase,
        placeholder=placeholder, representation=representation,
        user_input=user_input, value=value
    ).get_value()


def input_enum(
    title: Any, enum: Union[type[ENUM], ENUM], *, clear: bool = False,
    confirm: bool = False, placeholder: Optional[str] = None,
    representation: type[str] = Representation
) -> Optional[ENUM]:
    """Read enum from console input."""
    return dict_picker(
        title, {
            item.name: item
            for item in (enum if isinstance(enum, type) else type(enum))
        }, clear=clear, confirm=confirm, make_uppercase=True,
        placeholder=placeholder, representation=representation,
        value=None if isinstance(enum, type) else enum
    )
