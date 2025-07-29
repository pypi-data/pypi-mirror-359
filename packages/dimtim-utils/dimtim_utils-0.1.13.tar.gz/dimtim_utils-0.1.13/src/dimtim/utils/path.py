import os


def fileext(name: str):
    """
    Returns the file extension of a given filename.

    Parameters:
        name (str): The filename to extract the extension from.

    Returns:
        str: The file extension (including the dot) of the given filename.

    Example:
        >>> fileext('example.txt')
        '.txt'
    """
    return os.path.splitext(name)[-1]
