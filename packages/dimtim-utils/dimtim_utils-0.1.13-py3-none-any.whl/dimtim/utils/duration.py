import datetime


def _get_duration_components(duration: datetime.timedelta):
    """
    Breaks down a timedelta object into its components.

    Parameters:
        duration (datetime.timedelta): The duration to break down.

    Returns:
        tuple: A tuple containing (days, hours, minutes, seconds, microseconds).
    """
    minutes = duration.seconds // 60
    seconds = duration.seconds % 60

    hours = minutes // 60
    minutes = minutes % 60

    return duration.days, hours, minutes, seconds, duration.microseconds


def duration_string(duration: datetime.timedelta):
    """
    Formats a timedelta as a human-readable string.

    Parameters:
        duration (datetime.timedelta): The duration to format.

    Returns:
        str: A formatted string in the format "d hh:mm:ss.microseconds".
             Days and microseconds are only included if non-zero.

    Example:
        >>> from datetime import timedelta
        >>> duration = timedelta(days=1, hours=2, minutes=30, seconds=45, microseconds=123456)
        >>> duration_string(duration)
        '1 02:30:45.123456'
    """
    days, hours, minutes, seconds, microseconds = _get_duration_components(duration)

    string = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    if days:
        string = f'{days} {string}'
    if microseconds:
        string += f'.{microseconds:06d}'

    return string


def duration_iso_string(duration: datetime.timedelta):
    """
    Formats a timedelta as an ISO 8601 duration string.

    Parameters:
        duration (datetime.timedelta): The duration to format.

    Returns:
        str: An ISO 8601 formatted duration string (e.g., "P1DT02H30M45.123456S").
             Negative durations are prefixed with a minus sign.

    Example:
        >>> from datetime import timedelta
        >>> duration = timedelta(days=1, hours=2, minutes=30, seconds=45, microseconds=123456)
        >>> duration_iso_string(duration)
        'P1DT02H30M45.123456S'
    """
    if duration < datetime.timedelta(0):
        sign = '-'
        duration *= -1
    else:
        sign = ''

    days, hours, minutes, seconds, microseconds = _get_duration_components(duration)
    ms = f'.{microseconds:06d}' if microseconds else ""
    return f'{sign}P{days}DT{hours:02d}H{minutes:02d}M{seconds:02d}{ms}S'


def duration_microseconds(delta):
    """
    Converts a timedelta to microseconds.

    Parameters:
        delta (datetime.timedelta): The duration to convert.

    Returns:
        int: The duration in microseconds.

    Example:
        >>> from datetime import timedelta
        >>> duration = timedelta(seconds=1, microseconds=500000)
        >>> duration_microseconds(duration)
        1500000
    """
    return (24 * 60 * 60 * delta.days + delta.seconds) * 1000000 + delta.microseconds
