def noop(*args, **kwargs):  # noqa
    """
    A no-operation function that does nothing.

    This function accepts any arguments and keyword arguments but does nothing with them.
    It's useful as a placeholder or default callback.

    Parameters:
        *args: Any positional arguments.
        **kwargs: Any keyword arguments.

    Returns:
        None

    Example:
        >>> from dimtim.utils import noop
        >>> noop()  # Does nothing
        >>> noop(1, 2, 3, name='value')  # Also does nothing
    """
    pass
