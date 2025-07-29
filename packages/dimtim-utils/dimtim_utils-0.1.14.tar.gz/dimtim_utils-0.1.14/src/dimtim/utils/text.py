import re
import unicodedata
from typing import Optional


def inline(value: str) -> str:
    """
    Convert a multi-line string to a single line by replacing newlines and indentation with spaces.

    Parameters:
        value (str): The string to convert.

    Returns:
        str: The input string with newlines and indentation replaced by spaces.

    Example:
        >>> text = '''This is a
        ...           multi-line
        ...           string'''
        >>> print(inline(text))  # Output: "This is a multi-line string"
    """
    return re.sub(r'\r?\n\s+', ' ', value).strip()


def slugify(value: str, allow_unicode: bool = False) -> str:
    """
    Convert a string to a URL-friendly slug.

    This function converts a string to lowercase, removes non-word characters,
    and replaces spaces with hyphens to create a URL-friendly slug.

    Parameters:
        value (str): The string to convert.
        allow_unicode (bool): If True, allow unicode characters in the slug.
                             If False, convert to ASCII. Default is False.

    Returns:
        str: A URL-friendly slug.

    Example:
        >>> print(slugify("Hello World!"))  # Output: "hello-world"
        >>> print(slugify("Привет, мир!", allow_unicode=True))  # Output: "привет-мир"
    """
    if allow_unicode:
        value = unicodedata.normalize('NFKC', str(value))
    else:
        value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', value.lower()).strip())


def strip_markdown(value: str) -> str:
    """
    Convert Markdown text to plain text by removing all formatting.

    This function converts Markdown to HTML and then extracts the plain text content.

    Parameters:
        value (str): The Markdown text to convert.

    Returns:
        str: Plain text with all Markdown formatting removed.

    Raises:
        ModuleNotFoundError: If the required libraries (beautifulsoup4 and markdown) are not installed.

    Example:
        >>> markdown_text = "# Heading\n\nThis is **bold** and *italic* text."
        >>> print(strip_markdown(markdown_text))  # Output: "Heading This is bold and italic text."
    """
    try:
        from bs4 import BeautifulSoup
        import markdown
    except ImportError:
        raise ModuleNotFoundError(f'Method "{strip_markdown.__name__}" requires "beautifulsoup4" and "markdown" libraries')

    return BeautifulSoup(markdown.markdown(value), 'html.parser').text


def to_snake_case(text: str) -> str:
    """
    Convert a string to snake_case.

    This function converts strings in camelCase or PascalCase to snake_case.

    Parameters:
        text (str): The string to convert.

    Returns:
        str: The string converted to snake_case.

    Example:
        >>> print(to_snake_case("helloWorld"))  # Output: "hello_world"
        >>> print(to_snake_case("HelloWorld"))  # Output: "hello_world"
    """
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)).lower()


def to_kebab_case(text: str) -> str:
    """
    Convert a string to kebab-case.

    This function converts strings in camelCase or PascalCase to kebab-case.

    Parameters:
        text (str): The string to convert.

    Returns:
        str: The string converted to kebab-case.

    Example:
        >>> print(to_kebab_case("helloWorld"))  # Output: "hello-world"
        >>> print(to_kebab_case("HelloWorld"))  # Output: "hello-world"
    """
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)).lower()


def to_camel_case(text: str) -> str:
    """
    Convert a string to CamelCase (PascalCase).

    This function converts strings with spaces, underscores, dots, or hyphens to CamelCase.

    Parameters:
        text (str): The string to convert.

    Returns:
        str: The string converted to CamelCase.

    Example:
        >>> print(to_camel_case("hello_world"))  # Output: "HelloWorld"
        >>> print(to_camel_case("hello-world"))  # Output: "HelloWorld"
        >>> print(to_camel_case("hello world"))  # Output: "HelloWorld"
    """
    return ''.join(word.capitalize() for word in re.split(r'[ ._-]', text, re.MULTILINE))


# Constants for file size conversion
KILOBYTE = 1024
MEGABYTE = 1048576  # 1024 * 1024
GIGABYTE = 1073741824  # 1024 * 1024 * 1024
TERABYTE = 1099511627776  # 1024 * 1024 * 1024 * 1024
PETABYTE = 1125899906842624  # 1024 * 1024 * 1024 * 1024 * 1024


def format_size(size: int) -> str:
    """
    Format a file size in bytes to a human-readable string.

    This function converts a size in bytes to a human-readable format with appropriate units
    (b, Kb, Mb, Gb, Tb) based on the size magnitude.

    Parameters:
        size (int): The size in bytes.

    Returns:
        str: A human-readable string representation of the size.

    Example:
        >>> print(format_size(1500))  # Output: "1.46 Kb"
        >>> print(format_size(1500000))  # Output: "1.43 Mb"
    """
    if size < KILOBYTE:
        return f'{size} b'
    if size < MEGABYTE:
        return f'{size / KILOBYTE:.2f} Kb'
    if size < GIGABYTE:
        return f'{size / MEGABYTE:.2f} Mb'
    if size < TERABYTE:
        return f'{size / GIGABYTE:.2f} Gb'
    if size < PETABYTE:
        return f'{size / TERABYTE:.2f} Tb'
    return str(size)


def normalize_email(email: str) -> Optional[str]:
    """
    Normalize an email address by converting it to lowercase.

    This function splits the email into local part and domain, converts both to lowercase,
    and rejoins them. It handles invalid email formats by returning None.

    Parameters:
        email (str): The email address to normalize.

    Returns:
        Optional[str]: The normalized email address, or None if the input is not a valid email.

    Example:
        >>> print(normalize_email("User@Example.COM"))  # Output: "user@example.com"
        >>> print(normalize_email("invalid-email"))  # Output: None
    """
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except (ValueError, AttributeError):
        return None
    return '@'.join([email_name.lower(), domain_part.lower()])


def normalize_username(username: str) -> str:
    """
    Normalize a username by applying Unicode normalization.

    This function applies NFKC normalization to ensure consistent representation
    of Unicode characters in usernames.

    Parameters:
        username (str): The username to normalize.

    Returns:
        str: The normalized username, or the original value if it's empty.

    Example:
        >>> print(normalize_username("Café"))  # Normalizes any composed Unicode characters
    """
    return unicodedata.normalize('NFKC', username) if username else username


def pluralize(locale: str, value: int, one: str, two: str, five: str) -> str:
    """
    Return the appropriate plural form of a word based on a number and locale.

    This function handles pluralization rules for English and Russian languages.

    Parameters:
        locale (str): The language code ('en' or 'ru').
        value (int): The number that determines which plural form to use.
        one (str): The form to use when value requires the singular form.
        two (str): The form to use for the second plural form.
        five (str): The form to use for the third plural form (only used in Russian).

    Returns:
        str: The appropriate plural form based on the value and locale.

    Raises:
        ValueError: If the locale is not supported.

    Example:
        >>> # English
        >>> print(pluralize('en', 1, 'apple', 'apples', ''))  # Output: "apple"
        >>> print(pluralize('en', 2, 'apple', 'apples', ''))  # Output: "apples"

        >>> # Russian
        >>> print(pluralize('ru', 1, 'яблоко', 'яблока', 'яблок'))  # Output: "яблоко"
        >>> print(pluralize('ru', 2, 'яблоко', 'яблока', 'яблок'))  # Output: "яблока"
        >>> print(pluralize('ru', 5, 'яблоко', 'яблока', 'яблок'))  # Output: "яблок"
    """
    if locale == 'en':
        return one if value == 1 else two

    if locale == 'ru':
        ones = value % 10
        tens = value % 100
        return one if (ones == 1 and tens != 11) else two if (2 <= ones <= 4 and (tens < 10 or tens >= 20)) else five

    raise ValueError(f'Unsupported locale "{locale}"')
