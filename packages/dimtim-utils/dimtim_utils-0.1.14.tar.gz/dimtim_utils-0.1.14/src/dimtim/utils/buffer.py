from io import BytesIO
from typing import Union


def named_bytesio(name: str, content: Union[str, bytes] = None) -> BytesIO:
    """
    Creates a BytesIO object with a name attribute.

    Parameters:
        name (str): The name to assign to the BytesIO object.
        content (Union[str, bytes], optional): The content to initialize the BytesIO object with. Default is None.

    Returns:
        BytesIO: A BytesIO object with a name attribute.

    Example:
        >>> buffer = named_bytesio('example.txt', b'Hello, world!')
        >>> buffer.name
        'example.txt'
        >>> buffer.getvalue()
        b'Hello, world!'
    """
    bio = BytesIO(content)
    bio.name = name
    return bio
