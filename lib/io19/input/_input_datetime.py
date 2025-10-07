"""19.io classes & functions for date, datetime, time & timedelta input."""
# Linting arguments
# pylint: disable=useless-suppression
# ...
# pylint: disable=too-many-branches, too-many-locals

# Standard libraries
from calendar import monthrange
from datetime import date, datetime, time, timedelta
from typing import Any, Optional, Union

# Custom libraries
from ..translate import gettext as _
from ._classes import Representation
from ._input_complex import input_int
from ._input_enum import dict_picker

__all__: list[str] = ['RelativeDate', 'RelativeDateTime', 'RelativeTime']
__all__ += ['input_date', 'input_datetime', 'input_time', 'input_timedelta']


RelativeDate = Union[date, timedelta]
RelativeDateTime = Union[date, time, timedelta]
RelativeTime = Union[time, timedelta]


def input_date(
    title: Any, *, clear: bool = False, max_date: RelativeDate = date.max,
    min_date: RelativeDate = date.min, placeholder: Optional[str] = None,
    representation: type[str] = Representation,
    value: Optional[RelativeDate] = None
) -> Optional[date]:
    """Read date from console input."""
    today: date = date.today()
    if isinstance(max_date, timedelta):
        max_date += today

    if isinstance(min_date, timedelta):
        min_date += today

    if isinstance(value, timedelta):
        value += today

    day_value: Optional[int] = None
    month_value: Optional[int] = None
    if not isinstance(value, date):
        pass
    elif not min_date <= value <= max_date:
        raise ValueError('value must lay between min_date & max_date')
    else:
        month_value, day_value = value.month, value.day

    if min_date > max_date:
        raise ValueError('min_date must be smaller than max_date')

    year: Optional[int] = input_int(
        title, clear=clear, max_value=max_date.year, min_value=min_date.year,
        placeholder=placeholder, representation=representation,
        value=None if value is None else value.year,
    )
    if year is None:
        return None

    max_month: int = 12 if year < max_date.year else max_date.month
    min_month: int = 1 if year > min_date.year else min_date.month
    # noinspection PyArgumentEqualDefault
    month_string: Optional[str] = dict_picker(
        _('Enter month:'), {
            f'{i:02d}': date(year, i, 1)
            for i in range(min_month, max_month + 1)
        }, clear=clear, key=f'{month_value:02d}',
        representation=representation, select_key=True
    )
    if month_string is None:
        return None

    month: int = int(month_string)
    max_day: int = (
        monthrange(year, month)[1] if month < max_month else max_date.day
    )
    min_day: int = 1 if month > min_month else min_date.day
    # noinspection PyArgumentEqualDefault
    day_string: Optional[str] = dict_picker(
        _('Enter day:'), {
            f'{i:02d}': date(year, month, i)
            for i in range(min_day, max_day + 1)
        }, clear=clear, key=f'{day_value:02d}', representation=representation,
        select_key=True
    )
    return None if day_string is None else date(year, month, int(day_string))


def input_time(
    title: Any, *, clear: bool = False, max_time: RelativeTime = time.max,
    min_time: RelativeTime = time.min, placeholder: Optional[str] = None,
    representation: type[str] = Representation,
    value: Optional[RelativeTime] = None
) -> Optional[time]:
    """Read time from console input."""
    now: datetime = datetime.now()
    if isinstance(max_time, timedelta):
        max_time = (max_time + now).time()

    if isinstance(min_time, timedelta):
        min_time = (min_time + now).time()

    if isinstance(value, timedelta):
        value = (value + now).time()

    minute_value: Optional[int] = None
    if not isinstance(value, time):
        pass
    elif not min_time <= value <= max_time:
        raise ValueError('value must lay between min_time & max_time')
    else:
        minute_value = value.minute

    if min_time > max_time:
        raise ValueError('min_time must be smaller than max_time')

    # noinspection PyArgumentEqualDefault
    hour_string: Optional[str] = dict_picker(
        title, {
            f'{i:02d}': time(i)
            for i in range(min_time.hour, max_time.hour + 1)
        }, clear=clear, key=None if value is None else f'{value.hour:02d}',
        placeholder=placeholder, representation=representation, select_key=True
    )
    if hour_string is None:
        return None

    hour: int = int(hour_string)
    max_minute: int = 59 if hour < max_time.hour else max_time.minute
    min_minute: int = 0 if hour > min_time.hour else min_time.minute
    # noinspection PyArgumentEqualDefault
    minute_string: Optional[str] = dict_picker(
        _('Enter minute:'), {f'{i:02d}': time(hour, i) for i in range(
            min_minute, max_minute + 1
        )}, clear=clear, key=f'{minute_value:02d}', placeholder=placeholder,
        representation=representation, select_key=True
    )
    return None if minute_string is None else time(hour, int(minute_string))


def input_datetime(  # noqa: MC0001
    title: Any, *, clear: bool = False,
    max_datetime: RelativeDateTime = date.max,
    min_datetime: RelativeDateTime = date.min,
    placeholder: Optional[str] = None,
    representation: type[str] = Representation,
    value: Optional[RelativeDate] = None
) -> Optional[datetime]:
    """Read datetime from console input."""
    now: datetime = datetime.now()
    if isinstance(max_datetime, date):
        max_datetime = datetime.combine(max_datetime, time.max)
    elif isinstance(max_datetime, time):
        max_datetime = datetime.combine(now.date(), max_datetime)
    elif isinstance(max_datetime, timedelta):
        max_datetime += now

    if isinstance(min_datetime, date):
        min_datetime = datetime.combine(min_datetime, time.min)
    elif isinstance(min_datetime, time):
        min_datetime = datetime.combine(now.date(), min_datetime)
    elif isinstance(min_datetime, timedelta):
        min_datetime += now

    if isinstance(value, date):
        value = datetime.combine(value, now.time())
    elif isinstance(value, time):
        value = datetime.combine(now.date(), value)
    elif isinstance(value, timedelta):
        value += now

    time_value: Optional[time] = None
    if value is None:
        pass
    elif not min_datetime <= value <= max_datetime:
        raise ValueError(
            'value must lay between min_datetime & max_datetime'
        )
    else:
        time_value = value.time()
        value = value.date()

    if min_datetime > max_datetime:
        raise ValueError('min_datetime must be smaller than max_datetime')

    result_date: Optional[date] = input_date(
        title, clear=clear, max_date=max_datetime.date(),
        min_date=min_datetime.date(), placeholder=placeholder,
        representation=representation, value=value
    )
    if result_date is None:
        return None

    max_time: time = (
        time.max if result_date <= min_datetime.date() else max_datetime.time()
    )
    min_time: time = (
        time.min if result_date >= max_datetime.date() else min_datetime.time()
    )
    result_time: Optional[time] = input_time(
        _('Enter time (hour):'), clear=clear, max_time=max_time,
        min_time=min_time, representation=representation, value=time_value
    )
    return None if result_time is None else datetime.combine(
        result_date, result_time
    )


def input_timedelta(
    title: Any, *, clear: bool = False,
    max_timedelta: timedelta = timedelta.max,
    min_timedelta: timedelta = timedelta.min,
    placeholder: Optional[str] = None,
    representation: type[str] = Representation,
    value: Optional[timedelta] = None
) -> Optional[timedelta]:
    """Read timedelta from console input."""
    hour_value: Optional[int] = None
    minute_value: Optional[int] = None
    if value is None:
        pass
    elif not min_timedelta <= value <= max_timedelta:
        raise ValueError(
            'value must lay betweeen min_timedelta & max_timedelta'
        )
    else:
        hour_value, minute_value = divmod(value.seconds // 60, 60)

    day: Optional[int] = input_int(
        title, clear=clear, max_value=max_timedelta.days,
        min_value=min_timedelta.days, placeholder=placeholder,
        representation=representation,
        value=None if value is None else value.days
    )
    if day is None:
        return None

    max_hour: int
    max_minute: int
    max_hour, max_minute = divmod(max_timedelta.seconds // 60, 60)
    min_hour: int
    min_minute: int
    min_hour, min_minute = divmod(min_timedelta.seconds // 60, 60)
    max_hour = 23 if day < max_timedelta.days else max_hour
    min_hour = 0 if day > min_timedelta.days else min_hour
    # noinspection PyArgumentEqualDefault
    hour_string: Optional[str] = dict_picker(
        _('Enter hour:'), {
            f'{i:02d}': timedelta(day, hours=i)
            for i in range(min_hour, max_hour + 1)
        }, clear=clear, key=f'{hour_value:02d}', representation=representation,
        select_key=True
    )
    if hour_string is None:
        return None

    hour: int = int(hour_string)
    max_minute = 59 if hour < max_hour else max_minute
    min_minute = 0 if hour > min_hour else min_minute
    # noinspection PyArgumentEqualDefault
    minute_string: Optional[str] = dict_picker(
        _('Enter minute:'), {
            f'{i:02d}': timedelta(day, minutes=i, hours=hour)
            for i in range(min_minute, max_minute + 1)
        }, clear=clear, key=f'{minute_value:02d}',
        representation=representation, select_key=True
    )
    return None if minute_string is None else timedelta(
        day, minutes=int(minute_string), hours=hour
    )
