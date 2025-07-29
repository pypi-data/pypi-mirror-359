import functools
import os
from contextlib import ContextDecorator
from datetime import date, datetime, time, timedelta, timezone, tzinfo
from typing import Optional, Union
from zoneinfo import ZoneInfo

from asgiref.local import Local

__all__ = [
    'utc', 'get_fixed_timezone', 'get_default_timezone', 'get_current_timezone', 'get_current_timezone_name',
    'get_default_timezone_name', 'activate', 'deactivate', 'override', 'localtime', 'localdate', 'now', 'is_aware', 'is_naive',
    'make_aware', 'make_naive', 'datetime', 'date', 'time', 'timezone', 'timedelta', 'tzinfo'
]

AnyDate = Union[datetime, date, time]

utc = timezone.utc


def get_fixed_timezone(offset: Union[timedelta, int]):
    if isinstance(offset, timedelta):
        offset = offset.total_seconds() // 60
    sign = '-' if offset < 0 else '+'
    hhmm = '%02d%02d' % divmod(abs(offset), 60)
    return timezone(timedelta(minutes=offset), sign + hhmm)


@functools.lru_cache()
def get_default_timezone():
    return ZoneInfo(os.environ.get('TIME_ZONE', 'Europe/Moscow'))


def get_default_timezone_name():
    return _get_timezone_name(get_default_timezone())


_active = Local()


def get_current_timezone():
    return getattr(_active, 'value', get_default_timezone())


def get_current_timezone_name():
    return _get_timezone_name(get_current_timezone())


def _get_timezone_name(timezone):
    return timezone.tzname(None) or str(timezone)


# Timezone selection functions.


def activate(timezone: str | tzinfo):
    if isinstance(timezone, tzinfo):
        _active.value = timezone
    elif isinstance(timezone, str):
        _active.value = ZoneInfo(timezone)
    else:
        raise ValueError(f'Invalid timezone: {timezone}')


def deactivate():
    if hasattr(_active, 'value'):
        del _active.value


class override(ContextDecorator):
    def __init__(self, timezone):
        self.timezone = timezone

    def __enter__(self):
        self.old_timezone = getattr(_active, 'value', None)
        if self.timezone is None:
            deactivate()
        else:
            activate(self.timezone)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.old_timezone is None:
            deactivate()
        else:
            _active.value = self.old_timezone


# Utilities

def localtime(value: datetime = None, timezone: tzinfo = None):
    if value is None:
        value = now()
    if timezone is None:
        timezone = get_current_timezone()
    if is_naive(value):
        raise ValueError('localtime() cannot be applied to a naive datetime')
    return value.astimezone(timezone)


def localdate(value: datetime = None, timezone: tzinfo = None):
    return localtime(value, timezone).date()


def now():
    return datetime.now(utc)


def is_aware(value: datetime):
    return value.utcoffset() is not None


def is_naive(value: datetime):
    return value.utcoffset() is None


def make_aware(value: datetime, timezone: tzinfo = None):
    if timezone is None:
        timezone = get_current_timezone()

    if isinstance(timezone, tzinfo):
        if value.tzinfo is not None:
            raise ValueError('Not naive datetime (tzinfo is already set)')
        return value.replace(tzinfo=timezone)

    if is_aware(value):
        raise ValueError(f'make_aware expects a naive datetime, got {value}')

    return value.replace(tzinfo=timezone)


def make_naive(value: datetime, timezone: tzinfo = None):
    if timezone is None:
        timezone = get_current_timezone()
    if is_naive(value):
        raise ValueError('make_naive() cannot be applied to a naive datetime')
    return value.astimezone(timezone).replace(tzinfo=None)


def parse(value: str, format: str, timezone: tzinfo = None) -> Optional[datetime]:
    return make_aware(datetime.strptime(value, format), timezone)


def has_overlap(start1: AnyDate, end1: AnyDate, start2: AnyDate, end2: AnyDate) -> bool:
    return max(start1, start2) <= min(end1, end2)
