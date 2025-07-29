import shutil
from io import IOBase
from typing import Callable, Optional

# Standard ANSI terminal colors
color_names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
# ANSI codes for foreground colors (text color)
foreground = {color_names[x]: '3%s' % x for x in range(8)}
# ANSI codes for background colors
background = {color_names[x]: '4%s' % x for x in range(8)}

# ANSI reset code to return to default formatting
RESET = '0'
# ANSI codes for text formatting options
opt_dict = {'bold': '1', 'underscore': '4', 'blink': '5', 'reverse': '7', 'conceal': '8'}


def colorize(text: str = '', opts=(), **kwargs) -> str:
    """
    Return your text, enclosed in ANSI graphics codes.

    Depends on the keyword arguments 'fg' and 'bg', and the contents of
    the opts tuple/list.

    Return the RESET code if no parameters are given.

    Valid colors:
        'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'

    Valid options:
        'bold'
        'underscore'
        'blink'
        'reverse'
        'conceal'
        'noreset' - string will not be auto-terminated with the RESET code

    Examples:
        >>> colorize('hello', fg='red', bg='blue', opts=('blink',))
        '\x1b[31;44;5mhello\x1b[0m'
        >>> colorize()
        '\x1b[0m'
        >>> colorize('goodbye', opts=('underscore',))
        '\x1b[4mgoodbye\x1b[0m'
        >>> print(colorize('first line', fg='red', opts=('noreset',)))
        \x1b[31mfirst line
        >>> print('this should be red too')
        this should be red too
        >>> print(colorize('and so should this'))
        \x1b[0mand so should this
        >>> print('this should not be red')
        this should not be red
    """
    code_list = []
    if text == '' and len(opts) == 1 and opts[0] == 'reset':
        return '\x1b[%sm' % RESET
    for k, v in kwargs.items():
        if k == 'fg':
            code_list.append(foreground[v])
        elif k == 'bg':
            code_list.append(background[v])
    for o in opts:
        if o in opt_dict:
            code_list.append(opt_dict[o])
    if 'noreset' not in opts:
        text = '%s\x1b[%sm' % (text or '', RESET)
    return '%s%s' % (('\x1b[%sm' % ';'.join(code_list)), text or '')


def make_style(opts=(), **kwargs) -> Callable[[str], str]:
    """
    Return a function with default parameters for colorize()

    Example:
        >>> bold_red = make_style(opts=('bold',), fg='red')
        >>> print(bold_red('hello'))
        \x1b[31;1mhello\x1b[0m
        >>> KEYWORD = make_style(fg='yellow')
        >>> COMMENT = make_style(fg='blue', opts=('bold',))
    """
    return lambda text: colorize(text, opts, **kwargs)


# Palette names for different terminal color schemes
NOCOLOR_PALETTE = 'nocolor'  # No colors, plain text
DARK_PALETTE = 'dark'        # Colors suitable for dark terminal backgrounds
LIGHT_PALETTE = 'light'      # Colors suitable for light terminal backgrounds

# Predefined color palettes for different message types
PALETTES = {
    NOCOLOR_PALETTE: {
        'ERROR': {},
        'SUCCESS': {},
        'WARNING': {},
        'INFO': {},
    },
    DARK_PALETTE: {
        'ERROR': {'fg': 'red', 'opts': ('bold',)},
        'SUCCESS': {'fg': 'green', 'opts': ('bold',)},
        'WARNING': {'fg': 'yellow', 'opts': ('bold',)},
        'INFO': {'fg': 'blue'}
    },
    LIGHT_PALETTE: {
        'ERROR': {'fg': 'red', 'opts': ('bold',)},
        'SUCCESS': {'fg': 'green', 'opts': ('bold',)},
        'WARNING': {'fg': 'yellow', 'opts': ('bold',)},
        'INFO': {'fg': 'blue'}
    }
}
# Default color palette to use if none is specified
DEFAULT_PALETTE = DARK_PALETTE


def show_progress(count: int, total: int, text: str = '', out: Optional[IOBase] = None):
    """
    Display a progress bar in the terminal.

    This function creates a visual progress bar that shows the current progress
    as a percentage and a graphical representation using block characters.
    The progress bar adapts to the current terminal width.

    Parameters:
        count (int): The current progress value.
        total (int): The total value representing 100% completion.
        text (str, optional): Text to display before the progress bar. Default is empty.
        out (IOBase, optional): A file-like object to write the progress bar to.
                               If None, prints to stdout. Default is None.

    Example:
        >>> import time
        >>> total_items = 100
        >>> for i in range(total_items + 1):
        ...     show_progress(i, total_items, "Processing:")
        ...     time.sleep(0.05)  # Simulate work
        >>> print()  # Add a newline after the progress is complete
    """
    text = f'{str(text)} ' if text else ''
    textlen, countlen, totallen = len(text), len(str(count)), len(str(total))
    maxlen = max(countlen, totallen)
    termwidth = shutil.get_terminal_size().columns - (textlen + maxlen + totallen + 10)
    rate = count / max(count, total)
    percents = termwidth * rate
    bars = ('█' * int(percents), '░' * int(termwidth - percents))
    msg = f'\r{text}[{count: <{totallen}}/{total: <{totallen}}][{int(rate * 100): >3}%% %s%s]' % bars

    if out:
        out.write(msg)
    else:
        print(msg, end='')
