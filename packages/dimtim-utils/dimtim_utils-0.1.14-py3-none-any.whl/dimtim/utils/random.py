import random
import secrets
import string
from typing import Sequence, TypeVar, Any

from dimtim.utils.data.wordlists import ADJECTIVES, NOUNS

# Character sets for random string generation
DEFAULT_CHARSET = string.ascii_letters + string.digits  # Letters and numbers
PASSWORD_CHARSET = DEFAULT_CHARSET + string.punctuation  # Letters, numbers, and special characters
UPPER_CHARSET = string.ascii_uppercase + string.digits  # Uppercase letters and numbers
HEX_CHARSET = string.hexdigits  # Hexadecimal characters (0-9, a-f, A-F)

T = TypeVar('T')


def get_random_string(length: int, charset: str = DEFAULT_CHARSET) -> str:
    """
    Generate a cryptographically secure random string of specified length.

    Parameters:
        length (int): The length of the string to generate.
        charset (str, optional): The set of characters to choose from.
                                Default is DEFAULT_CHARSET (letters and digits).

    Returns:
        str: A random string of the specified length.

    Example:
        >>> # Generate a random string of length 10
        >>> random_str = get_random_string(10)
        >>> print(random_str)  # e.g., "a7Bf9cD3e2"

        >>> # Generate a random password with special characters
        >>> password = get_random_string(12, PASSWORD_CHARSET)
        >>> print(password)  # e.g., "x8!K@p2&zL*q"
    """
    return ''.join(secrets.choice(charset) for _ in range(length))


def string4() -> str:
    """
    Generate a random string of length 4 using letters and digits.

    Returns:
        str: A random 4-character string.

    Example:
        >>> print(string4())  # e.g., "a7Bf"
    """
    return get_random_string(4, DEFAULT_CHARSET)


def string8() -> str:
    """
    Generate a random string of length 8 using letters and digits.

    Returns:
        str: A random 8-character string.

    Example:
        >>> print(string8())  # e.g., "a7Bf9cD3"
    """
    return get_random_string(8, DEFAULT_CHARSET)


def string16() -> str:
    """
    Generate a random string of length 16 using letters and digits.

    Returns:
        str: A random 16-character string.

    Example:
        >>> print(string16())  # e.g., "a7Bf9cD3e2G5h8J1"
    """
    return get_random_string(16, DEFAULT_CHARSET)


def string32() -> str:
    """
    Generate a random string of length 32 using letters and digits.

    Returns:
        str: A random 32-character string.

    Example:
        >>> print(string32())  # A random 32-character string
    """
    return get_random_string(32, DEFAULT_CHARSET)


def string64() -> str:
    """
    Generate a random string of length 64 using letters and digits.

    Returns:
        str: A random 64-character string.

    Example:
        >>> print(string64())  # A random 64-character string
    """
    return get_random_string(64, DEFAULT_CHARSET)


def hex4() -> str:
    """
    Generate a random hexadecimal string of length 4.

    Returns:
        str: A random 4-character hexadecimal string.

    Example:
        >>> print(hex4())  # e.g., "a7bf"
    """
    return get_random_string(4, HEX_CHARSET)


def hex8() -> str:
    """
    Generate a random hexadecimal string of length 8.

    Returns:
        str: A random 8-character hexadecimal string.

    Example:
        >>> print(hex8())  # e.g., "a7bf9cd3"
    """
    return get_random_string(8, HEX_CHARSET)


def hex16() -> str:
    """
    Generate a random hexadecimal string of length 16.

    Returns:
        str: A random 16-character hexadecimal string.

    Example:
        >>> print(hex16())  # e.g., "a7bf9cd3e2g5h8j1"
    """
    return get_random_string(16, HEX_CHARSET)


def hex32() -> str:
    """
    Generate a random hexadecimal string of length 32.

    Returns:
        str: A random 32-character hexadecimal string.

    Example:
        >>> print(hex32())  # A random 32-character hexadecimal string
    """
    return get_random_string(32, HEX_CHARSET)


def hex64() -> str:
    """
    Generate a random hexadecimal string of length 64.

    Returns:
        str: A random 64-character hexadecimal string.

    Example:
        >>> print(hex64())  # A random 64-character hexadecimal string
    """
    return get_random_string(64, HEX_CHARSET)


def string8upper() -> str:
    """
    Generate a random string of length 8 using uppercase letters and digits.

    Returns:
        str: A random 8-character string with uppercase letters and digits.

    Example:
        >>> print(string8upper())  # e.g., "A7BF9CD3"
    """
    return get_random_string(8, UPPER_CHARSET)


def username(underscores: bool = True) -> str:
    """
    Generate a random username using adjectives and nouns.

    This function creates a username in the format "adjective_adjective_noun"
    or "AdjectiveAdjectiveNoun" depending on the underscores parameter.

    Parameters:
        underscores (bool, optional): If True, separates words with underscores.
                                     If False, uses CamelCase. Default is True.

    Returns:
        str: A random username.

    Example:
        >>> print(username())  # e.g., "happy_brave_tiger"
        >>> print(username(False))  # e.g., "HappyBraveTiger"
    """
    if underscores:
        return f'{random.choice(ADJECTIVES)}_{random.choice(ADJECTIVES)}_{random.choice(NOUNS)}'
    return f'{random.choice(ADJECTIVES).capitalize()}{random.choice(ADJECTIVES).capitalize()}{random.choice(NOUNS).capitalize()}'


def choice(variants: Sequence[T]) -> T:
    """
    Choose a random element from a sequence.

    Parameters:
        variants (Sequence[T]): The sequence to choose from.

    Returns:
        T: A randomly selected element from the sequence.

    Example:
        >>> colors = ['red', 'green', 'blue', 'yellow']
        >>> print(choice(colors))  # e.g., "blue"
    """
    return random.choice(variants)
