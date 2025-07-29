import sys
import time
from contextlib import ContextDecorator
from typing import Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    import logging
    from dimtim.helpers import Logger


class timeit(ContextDecorator):
    """
    A context decorator for measuring execution time of code blocks.

    This class can be used as a context manager or as a decorator to measure
    the execution time of code blocks. The time is output to stdout or a logger.

    Parameters:
        tag (str): A tag to identify the timing in the output. Default is '-'.
        out (Logger, optional): A logger to output the timing information. If None, prints to stdout.

    Example:
        >>> # As a context manager
        >>> with timeit('database-query'):
        ...     # Code to measure
        ...     result = db.execute_query()

        >>> # As a decorator
        >>> @timeit('slow-function')
        ... def process_data():
        ...     # Code to measure
        ...     return processed_data
    """
    def __init__(self, tag: str = '-', out: Optional[Union['Logger', 'logging.Logger']] = None):
        self.tag = tag
        self.out = out

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start

        if duration < 1:
            formatted = f'{round(duration * 1000, 8)} ms'
        elif duration < 60:
            formatted = f'{round(duration, 8)} s'
        else:
            formatted = f'{round(duration / 60, 8)} m'

        message = f'EXECUTION TIME :: {self.tag} :: {formatted}'
        if self.out:
            self.out.debug(message)
        else:
            sys.stdout.write(f'{message}\n')
        return False
