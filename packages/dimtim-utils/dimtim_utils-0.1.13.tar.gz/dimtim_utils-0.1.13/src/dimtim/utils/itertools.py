from typing import Sequence, Iterator, TypeVar

T = TypeVar('T')


def chunked(value: Sequence[T], size: int) -> Iterator[Sequence[T]]:
    """
    Split a sequence into chunks of a specified size.

    This function yields consecutive chunks from the input sequence,
    each of the specified size (except possibly the last chunk, which may be smaller).

    Parameters:
        value (Sequence[T]): The sequence to split into chunks.
        size (int): The size of each chunk.

    Yields:
        Sequence[T]: Chunks of the original sequence.

    Example:
        >>> # Split a list into chunks of size 3
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8]
        >>> for chunk in chunked(data, 3):
        ...     print(chunk)
        [1, 2, 3]
        [4, 5, 6]
        [7, 8]
    """
    for i in range(0, len(value), size):
        yield value[i:i + size]
