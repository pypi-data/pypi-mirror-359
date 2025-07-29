import os
from typing import Any, Optional, Type, Union


def to_bool(value: Union[str, int, bool]) -> bool:
    """
    Convert a value to a boolean.

    This function converts various types of values to boolean:
    - Strings: 'true', 't', '1' (case-insensitive) are considered True
    - Other types: Uses Python's built-in bool() function

    Parameters:
        value (Union[str, int, bool]): The value to convert.

    Returns:
        bool: The boolean representation of the value.

    Example:
        >>> to_bool('true')  # Output: True
        True
        >>> to_bool('FALSE')  # Output: False
        False
        >>> to_bool(1)  # Output: True
        True
        >>> to_bool(0)  # Output: False
        False
    """
    if isinstance(value, str):
        return value.lower() in ('true', 't', '1')
    return bool(value)


def to_int(value: Union[str, int], default: int = None) -> Optional[int]:
    """
    Convert a value to an integer, with a fallback default.

    Parameters:
        value (Union[str, int]): The value to convert.
        default (int, optional): The default value to return if conversion fails.
                                Default is None.

    Returns:
        Optional[int]: The integer representation of the value, or the default if conversion fails.

    Example:
        >>> to_int('123')  # Output: 123
        123
        >>> to_int('abc', 0)  # Output: 0 (default)
        0
        >>> to_int(None)  # Output: None (default)
        None
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_list(value: str, cast: Type = None, separator: str = ',') -> list[Any]:
    """
    Convert a string to a list by splitting on a separator.

    Parameters:
        value (str): The string to convert.
        cast (Type, optional): A function to apply to each element of the list.
                              Default is None (no casting).
        separator (str, optional): The string to split on. Default is ','.

    Returns:
        list[Any]: The list of values, optionally cast to the specified type.

    Example:
        >>> print(to_list('a,b,c'))  # Output: ['a', 'b', 'c']
        ['a', 'b', 'c']
        >>> print(to_list('1,2,3', int))  # Output: [1, 2, 3]
        [1, 2, 3]
        >>> print(to_list('a;b;c', separator=';'))  # Output: ['a', 'b', 'c']
        ['a', 'b', 'c']
    """
    result = []
    if isinstance(value, str):
        result = [v for v in value.split(separator) if v]
    return [cast(v) for v in result] if callable(cast) else result


def get(name: str, default: str = None) -> str:
    """
    Get a string value from an environment variable.

    Parameters:
        name (str): The name of the environment variable.
        default (str, optional): The default value to return if the variable is not set.
                               Default is None.

    Returns:
        str: The value of the environment variable, or the default.

    Example:
        >>> # Assuming API_KEY=abc123 in the environment
        >>> print(get('API_KEY'))  # Output: abc123
        abc123
        >>> # Assuming SECRET is not set in the environment
        >>> print(get('SECRET', 'default-secret'))  # Output: default-secret
        default-secret
    """
    return os.environ.get(name) or default


def get_bool(name: str, default: bool = False) -> bool:
    """
    Get a boolean value from an environment variable.

    Parameters:
        name (str): The name of the environment variable.
        default (bool, optional): The default value to return if the variable is not set or cannot be converted to a boolean. Default is False.

    Returns:
        bool: The boolean value of the environment variable, or the default.

    Example:
        >>> # Assuming DEBUG=true in the environment
        >>> print(get_bool('DEBUG'))  # Output: True
        True
        >>> # Assuming VERBOSE is not set in the environment
        >>> print(get_bool('VERBOSE', True))  # Output: True (default)
        True
    """
    return to_bool(os.environ.get(name)) or default


def get_int(name: str, default: int = None) -> int | None:
    """
    Get an integer value from an environment variable.

    Parameters:
        name (str): The name of the environment variable.
        default (int, optional): The default value to return if the variable is not set
                                or cannot be converted to an integer. Default is None.

    Returns:
        int | None: The integer value of the environment variable, or the default.

    Example:
        >>> # Assuming PORT=8080 in the environment
        >>> get_int('PORT')  # Output: 8080
        8080

        >>> # Assuming TIMEOUT is not set in the environment
        >>> get_int('TIMEOUT', 30)  # Output: 30 (default)
        30
    """
    return val if (val := to_int(os.environ.get(name))) is not None else default


def get_list(name: str, cast: Type = None, separator: str = ',', default: list[Any] = None) -> list[Any]:
    """
    Get a list value from an environment variable.

    Parameters:
        name (str): The name of the environment variable.
        cast (Type, optional): A function to apply to each element of the list.
                              Default is None (no casting).
        separator (str, optional): The string to split on. Default is ','.
        default (list[Any], optional): The default value to return if the variable is not set
                                      or is empty. Default is an empty list.

    Returns:
        list[Any]: The list value from the environment variable, or the default.

    Example:
        >>> # Assuming ALLOWED_HOSTS=localhost,example.com in the environment
        >>> get_list('ALLOWED_HOSTS')  # Output: ['localhost', 'example.com']
        ['localhost', 'example.com']

        >>> # Assuming PORTS=8080,8081,8082 in the environment
        >>> get_list('PORTS', int)  # Output: [8080, 8081, 8082]
        [8080, 8081, 8082]

        >>> # Assuming TAGS is not set in the environment
        >>> get_list('TAGS', default=['default'])  # Output: ['default']
        ['default']
    """
    return val if (val := to_list(os.environ.get(name), cast, separator)) else (default or [])
