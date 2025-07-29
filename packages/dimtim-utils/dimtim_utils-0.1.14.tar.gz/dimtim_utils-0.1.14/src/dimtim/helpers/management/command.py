import sys
from argparse import ArgumentParser

from dimtim.helpers.logger import Logger


class CommandError(Exception):
    """
    Exception raised when a command encounters an error during execution.

    This exception is caught by the command's run method and displayed to the user.
    """
    pass


class CommandBase:
    """
    A base class for defining tasks.

    This class provides the foundation for creating command-line tasks. Subclasses
    should define the `help` attribute and implement the `handle` method.

    Attributes:
        help (str): A brief description of the command, displayed in help text.

    Example:
        from dimtim.helpers.management.command import CommandBase
        from argparse import ArgumentParser

        class Command(CommandBase):
            help = 'A sample task that greets a person'

            def add_arguments(self, parser: ArgumentParser):
                parser.add_argument('--name', '-n', default='World', help='Name to greet')

            def handle(self, **kwargs):
                name = kwargs.get('name', 'World')
                self.stdout.write(f"Hello, {name}!")
    """
    help = '...'

    def __init__(self, root: str):
        """
        Initialize a new CommandBase instance.

        Parameters:
            root (str): The root directory of the project.
        """
        self.stdin, self.stdout, self.stderr = sys.stdin, sys.stdout, sys.stderr

        self.root = root
        self.name = self.__module__.split('.')[-1]
        self.logger = Logger('management', f'{self.name}: ', self.stdout)

    def add_arguments(self, parser: ArgumentParser):
        """
        Add command-line arguments to the parser.

        This method should be overridden by subclasses to add command-specific
        arguments to the parser.

        Parameters:
            parser (ArgumentParser): The argument parser to add arguments to.
        """
        pass

    def run(self, args):
        """
        Run the task with the given arguments.

        This method parses the command-line arguments and calls the handle method
        with the parsed arguments as keyword arguments.

        Parameters:
            args (list): The command-line arguments.

        Raises:
            CommandError: If an error occurs during command execution.
            KeyboardInterrupt: If the command is interrupted by the user.
        """
        parser = ArgumentParser(description=self.help)
        self.add_arguments(parser)
        try:
            self.handle(**vars(parser.parse_args(args)))
        except KeyboardInterrupt:
            sys.stderr.write(f'Commad interrupted...\n')
        except CommandError as e:
            sys.stderr.write(f'{str(e)}\n')

    def handle(self, **kwargs):
        """
        Handle the task execution.

        This method must be implemented by subclasses to define the task's behavior.

        Parameters:
            **kwargs: The parsed command-line arguments.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError('A subclass of the CommandBase class must implement the "handle" method!')
