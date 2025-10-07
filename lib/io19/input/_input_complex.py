"""19.io classes & functions for dealing with number input."""
# TODO - support integer literals (0b/0B, 0o/0O/0, or 0x/0X)

# Linting arguments
# pylint: disable=useless-suppression
# ...
# pylint: disable=too-many-instance-attributes, too-many-branches
# pylint: disable=too-many-locals, too-many-statements

# Standard libraries
import sys
from cmath import inf, infj
from locale import atof, localeconv
from math import ceil, isnan, log
from string import ascii_lowercase, digits
from typing import Any, Optional, Union

# Custom libraries
from ..output.colors import dim
from ..real2float import Number, Real, format_real, real2float
from ..translate import gettext as _
from ._classes import Representation
from ._input_bytes import BaseInputStr
from ._input_enum import dict_picker

__all__: list[str] = ['InputFloat', 'InputInt']
__all__ += ['input_bool', 'input_complex', 'input_float', 'input_int']
_GROUP_SIZE: int = 3
_MAX_BASE: int = 36
_MAX_FLOAT_LENGTH: int = 310
_MIN_BASE: int = 2
_affinity: str = 'affinity'  # Characters of nan & infinity
_fifty: str = 'fifty'  # Characters exclusive to infinity


class InputFloat(BaseInputStr[float]):
    """Input float in locale formatting."""

    def __init__(
        self, title: Any, *, allow_nan: bool = True, clear: bool = False,
        max_value: Real = inf, min_value: Real = -inf,
        placeholder: Optional[str] = None,
        representation: type[str] = Representation,
        value: Optional[Real] = None
    ) -> None:
        """Make new InputFloat instance."""
        affinity_strings: list[str] = []
        if allow_nan:
            affinity_strings.extend(['nan', '-nan', '+nan'])

        max_value = real2float(max_value)
        if max_value == inf:
            affinity_strings.extend(['infinity', '+infinity'])

        min_value = real2float(min_value)
        if min_value == -inf:
            affinity_strings.append('-infinity')

        decimal_point: Union[int, list[int], str] = (
            localeconv()['decimal_point']
        )
        if not isinstance(decimal_point, str):
            raise RuntimeError(
                'locale.localeconv()["decimal_point"] must be a str'
            )

        self.decimal_point: str = decimal_point
        thousands_separator: Union[int, list[int], str] = (
            localeconv()['thousands_sep']
        )
        if not isinstance(thousands_separator, str):
            raise RuntimeError(
                'locale.localeconv()["thousands_sep"] must be a str'
            )

        self.thousands_separator: str = thousands_separator
        newvalue: Optional[str] = None
        if value is not None:
            if not (
                -inf <= min_value <= value <= max_value <= inf or
                isnan(value) and allow_nan
            ):
                raise ValueError(
                    'value must lay between min_value and max_value'
                )

            newvalue = self.format_float(value, True)

        if not -inf <= min_value <= max_value <= inf:
            raise ValueError('min_value is not smaller than max_value')

        self.affinity_strings: list[str] = affinity_strings
        self.allow_nan: bool = allow_nan
        self.max_value: float = max_value
        self.min_value: float = min_value
        super().__init__(
            title, clear=clear, make_lowercase=True,
            max_length=_MAX_FLOAT_LENGTH, placeholder=(
                _('Use float digits') if placeholder is None else placeholder
            ), representation=representation, value=newvalue,
            white_list=f'-+{self.decimal_point}eE' + digits + _affinity
        )

    def process_input(self, user_input: str) -> Optional[str]:  # noqa: MC0001
        """Process user input, return display input."""
        display_input: str
        length: int = len(user_input)
        for affinity_string in (
            [] if user_input in ['', '-', '+'] else self.affinity_strings
        ):
            display_input = ''
            i: int = 0
            self.cursor_back, self.processed_input = self.moved_back, ''
            for character in affinity_string:
                if i >= length:
                    pass
                elif user_input[i].lower() == character:
                    self.processed_input += user_input[i]
                    display_input += user_input[i]
                    i += 1
                    continue
                elif user_input[i].lower() not in affinity_string:
                    break

                if self.make_uppercase:
                    character = character.upper()

                self.processed_input += character
                display_input += dim(character)
                self.cursor_back += 1 if self.cursor_back + i >= length else 0
            else:
                if i >= length:
                    return display_input

        display_input = ''
        has_exponent_character: bool = False
        before_dot: Optional[str] = None
        missing_exponent: bool = True
        missing_mantissa: bool = True
        self.processed_input = ''
        for i, character in enumerate(user_input):
            if character in ['+', '-']:
                if self.processed_input and not has_exponent_character:
                    if before_dot is None:
                        before_dot = self.processed_input

                    if missing_mantissa:
                        display_input += dim(0)
                        self.processed_input += '0'
                        missing_mantissa = False
                        if self.cursor_back + i >= length:
                            self.cursor_back += 1

                    display_input += dim('e')
                    self.processed_input += 'e'
                    has_exponent_character = True
                    if self.cursor_back + i >= length:
                        self.cursor_back += 1
            elif character.lower() == 'e':
                has_exponent_character = True
                if before_dot is None:
                    before_dot = self.processed_input

                if missing_mantissa:
                    display_input += dim(0)
                    self.processed_input += '0'
                    missing_mantissa = False
                    if self.cursor_back + i >= length:
                        self.cursor_back += 1
            elif character == self.decimal_point:
                before_dot = self.processed_input
            elif has_exponent_character:
                missing_exponent = False
            else:
                missing_mantissa = False

            display_input += character
            self.processed_input += character

        before_dot = self.processed_input if before_dot is None else before_dot
        if missing_mantissa or has_exponent_character and missing_exponent:
            display_input += dim(0)
            self.processed_input += '0'
            self.cursor_back += 1

        self.suggestion_input = self.processed_input
        if not self.thousands_separator:
            return display_input

        dot_index: int = len(before_dot)
        display_input = display_input[dot_index:]
        self.processed_input = self.processed_input[dot_index:]
        sign: str = ''
        if before_dot[:1] in ['-', '+']:
            before_dot, sign = before_dot[1:], before_dot[:1]

        self.cursor_back += min(
            max(0, self.moved_back + dot_index - length), max(0, dot_index - 1)
        ) // _GROUP_SIZE
        groups: list[str] = [
            before_dot[max(0, i - _GROUP_SIZE):i]
            for i in reversed(range(dot_index, 0, -_GROUP_SIZE))
        ]
        self.processed_input = sign + '_'.join(groups) + self.processed_input
        return (
            sign + dim(self.thousands_separator).join(groups) +
            display_input
        )

    def format_float(self, value: Real, is_input: bool = False) -> str:
        """Format float using locale."""
        return (
            f'{format_real(value, "")}' if is_input else
            f'{format_real(value, ",")}').translate({
                ord(','): self.thousands_separator,
                ord('.'): self.decimal_point
            }
        )

    def validate_user_input(self, processed_input: str) -> Optional[str]:
        """Validate user input, return error message."""
        value: float = atof(processed_input)
        if value < self.min_value:
            return _('Value is {0} too small.').format(
                self.format_float(self.min_value - value)
            )

        if value > self.max_value:
            return _('Value is {0} too big.').format(
                self.format_float(value - self.max_value)
            )

        return None

    def is_affinity(self, user_input: str) -> bool:
        """Is user input is a valid affinity subsequence."""
        affinity_string: str
        for affinity_string in self.affinity_strings:
            character: str
            i: int = 0
            for character in affinity_string:
                if i >= len(user_input):
                    continue

                if user_input[i] not in affinity_string:
                    break

                i += 1 if user_input[i] == character else 0
            else:
                if i >= len(user_input):
                    return True

        return False

    def can_extend_user_input(
        self, user_input: str, char: str, moved_back: int
    ) -> bool:
        """Must the user input be extended."""
        length: int = len(user_input)
        after: str = user_input[length - moved_back:]
        before: str = user_input[:length - moved_back]
        if (
            user_input not in ['', '-', '+'] and self.is_affinity(user_input)
        ):
            # The current user input is a valid affinity subsequence, the new
            # user input should still be one
            return (
                char in '-+' + _affinity and
                self.is_affinity(before + char + after)
            )

        # Check for invalid input
        return not (
            char in '-+' and (
                # Check if an mantissa / exponent sign can be inserted
                user_input.count('-') + user_input.count('+') >= 2 or
                'e' in before[:-1] or
                before and (
                    '-' in user_input[1:] or '+' in user_input[1:]
                ) or (before or after[:1] in ['-', '+']) and (
                    self.decimal_point in after or 'e' in after
                )
            ) or char == self.decimal_point and (
                # Check if the decimal point can be inserted
                self.decimal_point in user_input or
                '-' in before[1:] or
                '+' in before[1:] or
                'e' in before or
                after.count('-') + after.count('+') >= 2 or
                after[:1] in ['-', '+'] and 'e' in after
            ) or char == 'e' and (
                # Check if the exponent character can be inserted
                'e' in user_input or
                before.count('-') + before.count('+') >= 2 or
                after.count('-') + after.count('+') >= 2 or
                '-' in after[1:] or
                '+' in after[1:] or
                self.decimal_point in after
            ) or char in digits and after[:1] in ['-', '+'] and (
                # Check if digits can be inserted
                before[-1:] == 'e' or
                '-' in after[1:] or
                '+' in after[1:] or
                self.decimal_point in after or
                'e' in after
            ) or char in _affinity and (
                # Check if new user input can become a valid affinity
                # subsequence
                char == 'a' and not self.allow_nan or (
                    char == 'n' and not self.allow_nan or char in _fifty
                ) and (user_input == '-' or self.max_value < inf) and (
                    user_input == '+' or self.min_value > -inf
                ) or user_input not in '-+' or
                after
            )
        )

    def submit(self) -> tuple[bool, Optional[float]]:
        """Submit value as result."""
        return True, atof(self.processed_input)


class InputInt(BaseInputStr[int]):
    """Input int as string."""

    def __init__(  # noqa: MC0001
        self, title: Any, *, base: int = 10, clear: bool = False,
        max_value: Optional[Real] = None, min_value: Optional[Real] = None,
        placeholder: Optional[str] = None,
        representation: type[str] = Representation, value: Optional[int] = None
    ) -> None:
        """Make new InputInt instance."""
        if not 2 <= _MIN_BASE <= base <= _MAX_BASE < inf:
            raise ValueError(
                f'base must lay between {_MIN_BASE} & {_MAX_BASE}'
            )

        self.base: int = base
        decimal_point: Union[int, list[int], str] = (
            localeconv()['decimal_point']
        )
        if not isinstance(decimal_point, str):
            raise RuntimeError(
                'locale.localeconv()["decimal_point"] must be a str'
            )

        self.decimal_point: str = decimal_point
        group_separator: str = ' '
        group_size: int = 3
        if base == 2:
            group_size = 4
        elif base == 10:
            thousands_separator: Union[int, list[int], str] = (
                localeconv()['thousands_sep']
            )
            if not isinstance(thousands_separator, str):
                raise RuntimeError(
                    'locale.localeconv()["thousands_sep"] must be a str'
                )

            group_separator = thousands_separator

        int_max_str_digits: Real = getattr(
            sys, 'get_int_max_str_digits', lambda: inf
        )()
        int_max_str_digits = int_max_str_digits if int_max_str_digits else inf
        abs_value: Real = base ** (int_max_str_digits - 1) - 1
        if max_value is None:
            max_value = abs_value
        elif not -inf <= -abs_value <= max_value <= abs_value <= inf:
            raise ValueError(
                'max_value must lay between 1 - base **' +
                'sys.get_int_max_str_digits() & base ** ' +
                'sys.get_int_max_str_digits() - 1'
            )

        if min_value is None:
            min_value = -abs_value
        elif not -inf <= -abs_value <= min_value <= abs_value <= inf:
            raise ValueError(
                'min_value must lay between 1 - base **' +
                'sys.get_int_max_str_digits() & base ** ' +
                'sys.get_int_max_str_digits() - 1'
            )

        max_length: Real = 1.0 + ceil(log(
            max(1.0, abs(min_value), abs(max_value)), base
        ))
        if not (
            max_value == inf or isinstance(max_value, int) or
            max_value.is_integer()
        ):
            raise ValueError('max_value must be a whole number / inf')

        if not (
            min_value == -inf or isinstance(min_value, int) or
            min_value.is_integer()
        ):
            raise ValueError('min_value must be a whole number / -inf')

        if not -inf <= min_value <= max_value <= inf:
            raise ValueError('min_value must be smaller than max_value')

        newvalue: Optional[str] = None
        if value is None:
            pass
        elif not -inf <= min_value <= value <= max_value <= inf:
            raise ValueError('value must lay between min_value & max_value')
        else:
            newvalue = self.format_int(value, True)

        self.group_separator: str = group_separator
        self.group_size: int = group_size
        self.max_value: Real = max_value
        self.min_value: Real = min_value
        super().__init__(
            title, clear=clear, make_lowercase=base != 16,
            make_uppercase=base == 16, max_length=max_length, placeholder=(
                _('Use digits') if placeholder is None else placeholder
            ), representation=representation, value=newvalue,
            white_list='-+' + (digits + ascii_lowercase)[:base]
        )

    def format_int(self, value: Real, is_input: bool = False) -> str:
        """Convert int to configured base."""
        if not is_input:
            return f'{format_real(value, ",")}'.translate({
                ord(','): self.group_separator,
                ord('.'): self.decimal_point
            })

        value = round(value)
        if not value:
            return '0'

        sign: str = '-' if value < 0 else ''
        value = abs(value)
        characters: list[str] = []
        while value:
            remainder: int
            value, remainder = divmod(value, self.base)
            if 0 <= remainder <= 9:
                characters.append(str(remainder))
            else:
                characters.append(chr(ord('a') + remainder - 10))

        return sign + ''.join(reversed(characters))

    def process_input(self, user_input: str) -> Optional[str]:
        """Process user input, return display input."""
        display_input: str = ''
        self.processed_input = ''
        value: str = user_input
        if user_input[:1] in ['-', '+']:
            display_input += user_input[:1]
            self.processed_input += user_input[:1]
            value = value[1:]

        if user_input[:1] != '-' and self.max_value <= 0:
            # Value should be less than zero
            display_input += dim('-')
            self.processed_input += '-'
            self.cursor_back += 1 if self.moved_back == len(user_input) else 0

        if user_input in '-+':
            # Empty string, or only sign
            self.processed_input += value + '0'
            self.cursor_back += 1
            return display_input + value + dim(0)

        # Valid integer
        self.suggestion_input = self.processed_input + value
        if not self.group_separator:
            self.processed_input += value
            return display_input + value

        length: int = max(0, len(value) - 1)
        self.cursor_back += min(self.moved_back, length) // self.group_size
        groups: list[str] = [
            value[max(0, i - self.group_size):i]
            for i in reversed(range(len(value), 0, -self.group_size))
        ]
        self.processed_input += '_'.join(groups)
        return display_input + dim(self.group_separator).join(groups)

    def validate_user_input(self, processed_input: str) -> Optional[str]:
        """Validate user input, return error message."""
        value: int = int(processed_input, self.base)
        if value < self.min_value:
            return _('Value is {0} too small.').format(
                self.format_int(self.min_value - value)
            )

        if value > self.max_value:
            return _('Value is {0} too big.').format(
                self.format_int(value - self.max_value)
            )

        return None

    def can_extend_user_input(
        self, user_input: str, char: str, moved_back: int
    ) -> bool:
        """Must the user input be extended."""
        length: int = len(user_input)
        after: str = user_input[length - moved_back:]
        before: str = user_input[:length - moved_back]
        return not (
            # Check if sign can be inserted
            char in '-+' and before or
            # Check if negative sign is allowed
            char == '-' and self.min_value >= 0 or
            # Check if positive sign is allowed
            char == '+' and self.max_value <= 0 or
            # Check if digit can be inserted
            after[:1] in ['-', '+']
        )

    def submit(self) -> tuple[bool, Optional[int]]:
        """Submit value as result."""
        return True, int(self.processed_input, self.base)


def input_bool(
    title: Any, *, clear: bool = False, confirm: bool = False,
    placeholder: Optional[str] = None,
    representation: type[str] = Representation, value: Optional[bool]
) -> Optional[bool]:
    """Read bool from console input."""
    return dict_picker(
        title, {
            0: False,
            1: True
        }, clear=clear, confirm=confirm, placeholder=placeholder,
        representation=representation, value=value
    )


def input_float(
    title: Any, *, allow_nan: bool = True, clear: bool = False,
    max_value: Real = inf, min_value: Real = -inf,
    placeholder: Optional[str] = None,
    representation: type[str] = Representation, value: Optional[Real] = None
) -> Optional[float]:
    """
    Read float from console input.

    TIP: Use `-sys.float_info.max` & `sys.float_info.max` for no infinity,
    `cmath.inf` & `cmath.nan` for affinity
    """
    return InputFloat(
        title, allow_nan=allow_nan, clear=clear, max_value=max_value,
        min_value=min_value, placeholder=placeholder,
        representation=representation, value=value
    ).get_value()


def input_int(
    title: Any, *, base: int = 10, clear: bool = False,
    max_value: Optional[Real] = None, min_value: Optional[Real] = None,
    placeholder: Optional[str] = None,
    representation: type[str] = Representation, value: Optional[int] = None
) -> Optional[int]:
    """
    Read int from console input.

    Note: Using not -e3299 < `max_value` < e3299 & not -e3299 < `min_value` <
    e3299 are not allowed on recent Python versions
    TIP: Use `sys.set_int_max_str_digits()` to increase the limit
    """
    return InputInt(
        title, base=base, clear=clear, max_value=max_value,
        min_value=min_value, placeholder=placeholder,
        representation=representation, value=value
    ).get_value()


def input_complex(
    title: Any, *, allow_nan: bool = True, clear: bool = False,
    max_value: Number = inf + infj, min_value: Number = -inf - infj,
    placeholder: Optional[str] = None,
    representation: type[str] = Representation, value: Optional[Number] = None
) -> Optional[complex]:
    """
    Read complex from console input.

    TIP: Use `-sys.float_info.max` & `sys.float_info.max` for no infinity,
    `cmath.inf`, `cmath.infj`, `cmath.nan` & `cmath.nanj` for affinity
    """
    if isinstance(max_value, int):
        max_value = real2float(max_value) + infj

    if isinstance(min_value, int):
        min_value = real2float(min_value)

    if isinstance(value, int):
        value = real2float(value)

    imag_value: Optional[float] = None
    if value is None:
        pass
    elif not (
        -inf <= min_value.imag <= value.imag <= max_value.imag <= inf or
        isnan(value.imag) and allow_nan
    ):
        raise ValueError(
            'value.imag must lay between min_value.imag and max_value.imag'
        )
    else:
        imag_value = value.imag
        value = value.real

    if not -inf <= min_value.imag <= max_value.imag <= inf:
        raise ValueError('min_value.imag must be smaller than max_value.imag')

    real: Optional[float] = input_float(
        title, allow_nan=allow_nan, clear=clear, max_value=max_value.real,
        min_value=min_value.real, placeholder=placeholder,
        representation=representation, value=value
    )
    if real is None:
        return None

    imag: Optional[float] = input_float(
        _('Enter imaginary part:'), allow_nan=allow_nan, clear=clear,
        max_value=max_value.imag, min_value=min_value.imag,
        placeholder=placeholder, representation=representation,
        value=imag_value
    )
    return None if imag is None else real + imag * 1j
