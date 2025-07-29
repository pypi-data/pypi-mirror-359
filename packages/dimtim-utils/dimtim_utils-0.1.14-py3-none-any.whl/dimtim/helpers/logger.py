import logging
from typing import Any, TextIO

from dimtim.utils.terminal import colorize


class Logger:
    """
    A wrapper around the standard logging module with additional features.

    This class provides a convenient interface for logging messages with different
    severity levels, and optionally displaying them in the console with color coding.

    Attributes:
        DEBUG (int): Debug level constant from logging module.
        INFO (int): Info level constant from logging module.
        WARNING (int): Warning level constant from logging module.
        ERROR (int): Error level constant from logging module.

    Example:
        >>> import sys
        >>> # Create a logger that outputs to both log file and stdout
        >>> logger = Logger('my-app', 'MyApp: ', sys.stdout)
        >>> # Log messages at different levels
        >>> logger.debug('Debug message')
        >>> logger.info('Info message')
        >>> logger.warning('Warning message')
        >>> logger.error('Error message')
    """
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

    def __init__(self, name: str = '', prefix: str = '', stdout: TextIO = None, stdprefix: str = ''):
        """
        Initialize a new Logger instance.

        Parameters:
            name (str): The name of the logger, used to get a logger instance from logging module.
            prefix (str): A prefix to add to all log messages.
            stdout (TextIO): A file-like object to write output to (e.g., sys.stdout).
            stdprefix (str): A prefix to add to all stdout messages.
        """
        self.logger = logging.getLogger(name)
        self.prefix = prefix
        self.stdout = stdout
        self.stdprefix = stdprefix

    def colorize(self, level: int, message: str) -> str:
        """
        Apply color to a message based on its log level.

        Parameters:
            level (int): The log level (DEBUG, INFO, WARNING, ERROR).
            message (str): The message to colorize.

        Returns:
            str: The colorized message.
        """
        color = {self.DEBUG: 'white', self.INFO: 'blue', self.WARNING: 'yellow', self.ERROR: 'red'}.get(level)
        return colorize(message, fg=color)

    def log(self, level: int, message: Any, prefix: str = '', stdprefix: str = '', nolog: bool = False, noout: bool = False, *args, **kwargs):
        """
        Log a message at the specified level.

        Parameters:
            level (int): The log level (DEBUG, INFO, WARNING, ERROR).
            message (Any): The message to log.
            prefix (str): A prefix to add to the log message, overrides the instance prefix if provided.
            stdprefix (str): A prefix to add to the stdout message, overrides the instance stdprefix if provided.
            nolog (bool): If True, the message will not be sent to the logger.
            noout (bool): If True, the message will not be written to stdout.
            *args: Additional positional arguments to pass to the logger.
            **kwargs: Additional keyword arguments to pass to the logger.
        """
        if not nolog:
            self.logger.log(level, f'{prefix or self.prefix}{message}', *args, **kwargs)
        if self.stdout and not noout:
            self.stdout.write(self.colorize(level, f'{stdprefix or self.stdprefix}{message}\n'))

    def debug(self, message: Any, prefix: str = '', stdprefix: str = '', nolog: bool = False, noout: bool = False, *args, **kwargs):
        """
        Log a message at DEBUG level.

        Parameters:
            message (Any): The message to log.
            prefix (str): A prefix to add to the log message, overrides the instance prefix if provided.
            stdprefix (str): A prefix to add to the stdout message, overrides the instance stdprefix if provided.
            nolog (bool): If True, the message will not be sent to the logger.
            noout (bool): If True, the message will not be written to stdout.
            *args: Additional positional arguments to pass to the logger.
            **kwargs: Additional keyword arguments to pass to the logger.
        """
        self.log(self.DEBUG, message, prefix, stdprefix, nolog, noout, *args, **kwargs)

    def info(self, message: Any, prefix: str = '', stdprefix: str = '', nolog: bool = False, noout: bool = False, *args, **kwargs):
        """
        Log a message at INFO level.

        Parameters:
            message (Any): The message to log.
            prefix (str): A prefix to add to the log message, overrides the instance prefix if provided.
            stdprefix (str): A prefix to add to the stdout message, overrides the instance stdprefix if provided.
            nolog (bool): If True, the message will not be sent to the logger.
            noout (bool): If True, the message will not be written to stdout.
            *args: Additional positional arguments to pass to the logger.
            **kwargs: Additional keyword arguments to pass to the logger.
        """
        self.log(self.INFO, message, prefix, stdprefix, nolog, noout, *args, **kwargs)

    def warning(self, message: Any, prefix: str = '', stdprefix: str = '', nolog: bool = False, noout: bool = False, *args, **kwargs):
        """
        Log a message at WARNING level.

        Parameters:
            message (Any): The message to log.
            prefix (str): A prefix to add to the log message, overrides the instance prefix if provided.
            stdprefix (str): A prefix to add to the stdout message, overrides the instance stdprefix if provided.
            nolog (bool): If True, the message will not be sent to the logger.
            noout (bool): If True, the message will not be written to stdout.
            *args: Additional positional arguments to pass to the logger.
            **kwargs: Additional keyword arguments to pass to the logger.
        """
        self.log(self.WARNING, message, prefix, stdprefix, nolog, noout, *args, **kwargs)

    def error(self, message: Any, prefix: str = '', stdprefix: str = '', nolog: bool = False, noout: bool = False, *args, **kwargs):
        """
        Log a message at ERROR level.

        Parameters:
            message (Any): The message to log.
            prefix (str): A prefix to add to the log message, overrides the instance prefix if provided.
            stdprefix (str): A prefix to add to the stdout message, overrides the instance stdprefix if provided.
            nolog (bool): If True, the message will not be sent to the logger.
            noout (bool): If True, the message will not be written to stdout.
            *args: Additional positional arguments to pass to the logger.
            **kwargs: Additional keyword arguments to pass to the logger.
        """
        self.log(self.ERROR, message, prefix, stdprefix, nolog, noout, *args, **kwargs)

    def exception(self, message: Any, prefix: str = '', stdprefix: str = '', nolog: bool = False, noout: bool = False, *args, exc_info: bool = True, **kwargs):
        """
        Log an exception at ERROR level with traceback information.

        Parameters:
            message (Any): The message to log.
            prefix (str): A prefix to add to the log message, overrides the instance prefix if provided.
            stdprefix (str): A prefix to add to the stdout message, overrides the instance stdprefix if provided.
            nolog (bool): If True, the message will not be sent to the logger.
            noout (bool): If True, the message will not be written to stdout.
            *args: Additional positional arguments to pass to the logger.
            exc_info (bool): If True, exception info is added to the logging message.
            **kwargs: Additional keyword arguments to pass to the logger.
        """
        self.error(message, prefix, stdprefix, nolog, noout, *args, exc_info=exc_info, **kwargs)
