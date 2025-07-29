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

# Type alias for date-like objects
AnyDate = Union[datetime, date, time]

# UTC timezone constant
utc = timezone.utc


def get_fixed_timezone(offset: Union[timedelta, int]):
    """
    Return a fixed timezone based on the given offset.

    Parameters:
        offset (Union[timedelta, int]): The offset from UTC in minutes or as a timedelta.

    Returns:
        timezone: A timezone object with the specified offset.

    Example:
        >>> # Create a timezone for UTC+3
        >>> tz = get_fixed_timezone(180)  # 180 minutes = 3 hours

        >>> # Or using timedelta
        >>> from datetime import timedelta
        >>> tz = get_fixed_timezone(timedelta(hours=3))
    """
    if isinstance(offset, timedelta):
        offset = offset.total_seconds() // 60
    sign = '-' if offset < 0 else '+'
    hhmm = '%02d%02d' % divmod(abs(offset), 60)
    return timezone(timedelta(minutes=offset), sign + hhmm)


@functools.lru_cache()
def get_default_timezone():
    """
    Return the default timezone for the application.

    This function returns a timezone based on the TIME_ZONE environment variable,
    or falls back to 'Europe/Moscow' if not set.

    Returns:
        ZoneInfo: The default timezone.

    Example:
        >>> default_tz = get_default_timezone()
        >>> print(default_tz)  # Output: Europe/Moscow (or the value of TIME_ZONE)
    """
    return ZoneInfo(os.environ.get('TIME_ZONE', 'Europe/Moscow'))


def get_default_timezone_name():
    """
    Return the name of the default timezone.

    Returns:
        str: The name of the default timezone.

    Example:
        >>> print(get_default_timezone_name())  # Output: "Europe/Moscow" (or the value of TIME_ZONE)
    """
    return _get_timezone_name(get_default_timezone())


# Thread-local storage for the active timezone
_active = Local()


def get_current_timezone():
    """
    Return the currently active timezone.

    If no timezone is active, returns the default timezone.

    Returns:
        tzinfo: The current timezone.

    Example:
        >>> # Activate a timezone
        >>> activate('US/Pacific')

        >>> # Get the current timezone
        >>> current_tz = get_current_timezone()
        >>> print(current_tz)  # Output: US/Pacific
    """
    return getattr(_active, 'value', get_default_timezone())


def get_current_timezone_name():
    """
    Return the name of the currently active timezone.

    Returns:
        str: The name of the current timezone.

    Example:
        >>> # Activate a timezone
        >>> activate('US/Pacific')

        >>> # Get the current timezone name
        >>> print(get_current_timezone_name())  # Output: "US/Pacific"
    """
    return _get_timezone_name(get_current_timezone())


def _get_timezone_name(timezone):
    """
    Return the name of the given timezone.

    Parameters:
        timezone (tzinfo): The timezone to get the name of.

    Returns:
        str: The name of the timezone.
    """
    return timezone.tzname(None) or str(timezone)


# Timezone selection functions.


def activate(timezone: str | tzinfo):
    """
    Activate a timezone for the current thread.

    This function sets the timezone to be used for all timezone-aware operations
    in the current thread.

    Parameters:
        timezone (str | tzinfo): The timezone to activate. Can be a timezone object
                                or a string name of a timezone.

    Raises:
        ValueError: If the timezone is not a valid timezone object or string.

    Example:
        >>> # Activate a timezone by name
        >>> activate('US/Pacific')
        >>> print(get_current_timezone_name())  # Output: "US/Pacific"

        >>> # Activate a timezone by object
        >>> from zoneinfo import ZoneInfo
        >>> activate(ZoneInfo('Europe/London'))
        >>> print(get_current_timezone_name())  # Output: "Europe/London"
    """
    if isinstance(timezone, tzinfo):
        _active.value = timezone
    elif isinstance(timezone, str):
        _active.value = ZoneInfo(timezone)
    else:
        raise ValueError(f'Invalid timezone: {timezone}')


def deactivate():
    """
    Deactivate the timezone for the current thread.

    This function removes any active timezone for the current thread,
    causing timezone-aware operations to use the default timezone.

    Example:
        >>> # Activate a timezone
        >>> activate('US/Pacific')
        >>> print(get_current_timezone_name())  # Output: "US/Pacific"

        >>> # Deactivate the timezone
        >>> deactivate()
        >>> print(get_current_timezone_name())  # Output: "Europe/Moscow" (or default)
    """
    if hasattr(_active, 'value'):
        del _active.value


class override(ContextDecorator):
    """
    A context manager and decorator for temporarily overriding the timezone.

    This class allows you to temporarily change the timezone within a context block
    or a decorated function, and automatically restore the previous timezone when done.

    Parameters:
        timezone (str | tzinfo | None): The timezone to use within the context.
                                       If None, deactivates the timezone.

    Example:
        >>> # As a context manager
        >>> print(get_current_timezone_name())  # Output: "Europe/Moscow" (or default)
        >>> with override('US/Pacific'):
        ...     print(get_current_timezone_name())  # Output: "US/Pacific"
        >>> print(get_current_timezone_name())  # Output: "Europe/Moscow" (or default)

        >>> # As a decorator
        >>> @override('US/Pacific')
        ... def my_function():
        ...     print(get_current_timezone_name())  # Output: "US/Pacific"
    """

    def __init__(self, timezone):
        """
        Initialize the override context manager.

        Parameters:
            timezone (str | tzinfo | None): The timezone to use within the context.
                                           If None, deactivates the timezone.
        """
        self.timezone = timezone

    def __enter__(self):
        """
        Enter the context and activate the specified timezone.

        Returns:
            self: The context manager instance.
        """
        self.old_timezone = getattr(_active, 'value', None)
        if self.timezone is None:
            deactivate()
        else:
            activate(self.timezone)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context and restore the previous timezone.

        Parameters:
            exc_type: The exception type, if an exception was raised.
            exc_value: The exception value, if an exception was raised.
            traceback: The traceback, if an exception was raised.

        Returns:
            bool: False to propagate exceptions, if any.
        """
        if self.old_timezone is None:
            deactivate()
        else:
            _active.value = self.old_timezone
        return False


# Utilities

def localtime(value: datetime = None, timezone: tzinfo = None):
    """
    Convert a datetime to the local time in the specified timezone.

    Parameters:
        value (datetime, optional): The datetime to convert. If None, uses the current time.
        timezone (tzinfo, optional): The timezone to convert to. If None, uses the current timezone.

    Returns:
        datetime: The datetime converted to the specified timezone.

    Raises:
        ValueError: If the input datetime is naive (has no timezone information).

    Example:
        >>> # Convert current UTC time to local time
        >>> utc_now = now()
        >>> local_now = localtime(utc_now)
        >>> print(local_now)  # Current time in the active timezone
    """
    if value is None:
        value = now()
    if timezone is None:
        timezone = get_current_timezone()
    if is_naive(value):
        raise ValueError('localtime() cannot be applied to a naive datetime')
    return value.astimezone(timezone)


def localdate(value: datetime = None, timezone: tzinfo = None):
    """
    Get the date in the specified timezone.

    This function converts a datetime to the specified timezone and returns just the date part.

    Parameters:
        value (datetime, optional): The datetime to convert. If None, uses the current time.
        timezone (tzinfo, optional): The timezone to convert to. If None, uses the current timezone.

    Returns:
        date: The date in the specified timezone.

    Example:
        >>> # Get today's date in the current timezone
        >>> today = localdate()
        >>> print(today)  # Today's date in the active timezone
    """
    return localtime(value, timezone).date()


def now():
    """
    Return the current datetime in UTC.

    Returns:
        datetime: The current datetime with UTC timezone.

    Example:
        >>> # Get current UTC time
        >>> utc_now = now()
        >>> print(utc_now)  # Current time in UTC
    """
    return datetime.now(utc)


def is_aware(value: datetime):
    """
    Determine if a datetime is timezone-aware.

    A datetime is timezone-aware if it has timezone information attached to it.

    Parameters:
        value (datetime): The datetime to check.

    Returns:
        bool: True if the datetime is timezone-aware, False otherwise.

    Example:
        >>> # Check if a datetime is timezone-aware
        >>> aware_dt = now()  # UTC-aware datetime
        >>> from datetime import datetime
        >>> naive_dt = datetime.now()  # Naive datetime

        >>> print(is_aware(aware_dt))  # Output: True
        >>> print(is_aware(naive_dt))  # Output: False
    """
    return value.utcoffset() is not None


def is_naive(value: datetime):
    """
    Determine if a datetime is timezone-naive.

    A datetime is timezone-naive if it has no timezone information attached to it.

    Parameters:
        value (datetime): The datetime to check.

    Returns:
        bool: True if the datetime is timezone-naive, False otherwise.

    Example:
        >>> # Check if a datetime is timezone-naive
        >>> aware_dt = now()  # UTC-aware datetime
        >>> from datetime import datetime
        >>> naive_dt = datetime.now()  # Naive datetime

        >>> print(is_naive(aware_dt))  # Output: False
        >>> print(is_naive(naive_dt))  # Output: True
    """
    return value.utcoffset() is None


def make_aware(value: datetime, timezone: tzinfo = None):
    """
    Make a naive datetime timezone-aware by attaching timezone information.

    Parameters:
        value (datetime): The naive datetime to make aware.
        timezone (tzinfo, optional): The timezone to attach. If None, uses the current timezone.

    Returns:
        datetime: The timezone-aware datetime.

    Raises:
        ValueError: If the input datetime is already timezone-aware.

    Example:
        >>> # Make a naive datetime timezone-aware
        >>> from datetime import datetime
        >>> naive_dt = datetime(2023, 1, 1, 12, 0, 0)  # Noon on Jan 1, 2023
        >>> aware_dt = make_aware(naive_dt)  # Now in the current timezone
        >>> print(aware_dt)
    """
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
    """
    Make an aware datetime naive by removing timezone information.

    This function first converts the datetime to the specified timezone,
    then removes the timezone information.

    Parameters:
        value (datetime): The aware datetime to make naive.
        timezone (tzinfo, optional): The timezone to convert to before making naive.
                                    If None, uses the current timezone.

    Returns:
        datetime: The naive datetime.

    Raises:
        ValueError: If the input datetime is already naive.

    Example:
        >>> # Make an aware datetime naive
        >>> aware_dt = now()  # UTC-aware datetime
        >>> naive_dt = make_naive(aware_dt)  # Now naive in the current timezone
        >>> print(naive_dt)
    """
    if timezone is None:
        timezone = get_current_timezone()
    if is_naive(value):
        raise ValueError('make_naive() cannot be applied to a naive datetime')
    return value.astimezone(timezone).replace(tzinfo=None)


def parse(value: str, format: str, timezone: tzinfo = None) -> Optional[datetime]:
    """
    Parse a string into a timezone-aware datetime.

    Parameters:
        value (str): The string to parse.
        format (str): The format string (as used by datetime.strptime).
        timezone (tzinfo, optional): The timezone to attach. If None, uses the current timezone.

    Returns:
        Optional[datetime]: The parsed timezone-aware datetime.

    Example:
        >>> # Parse a date string into a timezone-aware datetime
        >>> dt = parse('2023-01-01 12:00:00', '%Y-%m-%d %H:%M:%S')
        >>> print(dt)  # 2023-01-01 12:00:00 in the current timezone
    """
    return make_aware(datetime.strptime(value, format), timezone)


def has_overlap(start1: AnyDate, end1: AnyDate, start2: AnyDate, end2: AnyDate) -> bool:
    """
    Check if two date/time ranges overlap.

    Parameters:
        start1 (AnyDate): The start of the first range.
        end1 (AnyDate): The end of the first range.
        start2 (AnyDate): The start of the second range.
        end2 (AnyDate): The end of the second range.

    Returns:
        bool: True if the ranges overlap, False otherwise.

    Example:
        >>> # Check if two time ranges overlap
        >>> from datetime import datetime
        >>> range1_start = datetime(2023, 1, 1, 10, 0)
        >>> range1_end = datetime(2023, 1, 1, 12, 0)
        >>> range2_start = datetime(2023, 1, 1, 11, 0)
        >>> range2_end = datetime(2023, 1, 1, 13, 0)

        >>> print(has_overlap(range1_start, range1_end, range2_start, range2_end))  # Output: True
    """
    return max(start1, start2) <= min(end1, end2)
