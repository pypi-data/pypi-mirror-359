import os
import pkgutil
import sys
import traceback
from typing import Callable, Type

from dimtim.helpers.management import CommandBase
from dimtim.utils import importing, terminal


class CommandRunner:
    """
    A class for managing and executing tasks.

    This class provides functionality to discover, list, and run tasks from a specified directory.
    Tasks are Python files with a Command class that inherits from CommandBase.

    Parameters:
        root (str): The root directory of the project.
        bin_path (str): The path to the directory containing task files, relative to the root.

    Example:
        from dimtim.helpers.management.runner import CommandRunner

        # Create a runner for the current directory with tasks in the 'bin' folder
        runner = CommandRunner('/path/to/project', 'bin')

        # Run a task
        runner.run('task-name', '--arg1', 'value1')

        # Set a global prepare hook
        CommandRunner.set_global_prepare_hook(lambda: print("Preparing to run a task..."))
    """
    prepare_hooks: list[Callable[[], None]] = []

    def __init__(self, root: str, bin_path: str):
        """
        Initialize a new CommandRunner instance.

        Parameters:
            root (str): The root directory of the project.
            bin_path (str): The path to the directory containing task files, relative to the root.
        """
        self.root = os.path.normpath(root)
        self.os_path = os.path.normpath(os.path.join(self.root, bin_path))
        self.py_path = os.path.relpath(self.os_path, self.root).replace(os.sep, '.').strip('.')
        sys.path.append(self.root)

    def collect_tasks(self) -> list[tuple[str, Type[CommandBase]]]:
        """
        Collects all available tasks from the bin_path directory.

        This method scans the bin_path directory for Python files that contain a Command class
        that inherits from CommandBase.

        Returns:
            list[tuple[str, Type[CommandBase]]]: A list of tuples containing the task name and the Command class.
        """
        result = []
        for finder, name, is_pkg in pkgutil.iter_modules([self.os_path]):
            try:
                _, module = importing.load_file_as_module(os.path.join(self.os_path, f'{name}.py'), name)
                if not is_pkg and (cls := getattr(module, 'Command', None)):
                    result.append((name, cls))
            except Exception as e:
                result.append((name, self._make_error_command_cls(e)))
        return result

    def available_tasks_string(self) -> str:
        """
        Returns a string listing all available tasks.

        This method formats a string that lists all available tasks with their help text,
        which is useful for displaying to the user.

        Returns:
            str: A formatted string listing all available tasks, or a message if no tasks are available.
        """
        if tasks := self.collect_tasks():
            max_name_length = max(len(name) for name, _ in tasks)
            result = []
            for name, command in tasks:
                task_name = terminal.colorize(name, ['bold'], fg='green')
                help_text = command.help
                result.append(f'    + {task_name} %s {help_text}' % ('-' * (max_name_length - len(name) + 1)))
            return 'Available tasks: \n%s\n' % '\n'.join(result)
        return f'No tasks available in {self.os_path}'

    def is_task_exists(self, name: str) -> bool:
        """
        Checks if a task with the given name exists.

        Parameters:
            name (str): The name of the task to check.

        Returns:
            bool: True if the task exists, False otherwise.
        """
        return os.path.exists(os.path.join(self.os_path, f'{name}.py'))

    def run(self, *args: str):
        """
        Runs a task with the given arguments.

        This method executes a task with the specified name and arguments. If no arguments
        are provided, it uses sys.argv[1:]. If no task name is provided, it displays a list
        of available tasks.

        Parameters:
            *args (str): The task name and its arguments. If empty, uses sys.argv[1:].

        Raises:
            SystemExit: If the task doesn't exist or there's an error loading it.
        """
        args = args or sys.argv[1:]

        try:
            importing.load_file_as_module(os.path.join(self.os_path, f'__init__.py'))
        except ImportError:
            pass

        for hook in self.prepare_hooks:
            hook()

        if args:
            task, *args = args

            if not self.is_task_exists(task):
                sys.stderr.write(f'Task "{task}" not found.\n{self.available_tasks_string()}')
                exit(-1)

            try:
                loader, module = importing.load_file_as_module(os.path.join(self.os_path, f'{task}.py'), execute=False)
            except ImportError as ex:
                sys.stderr.write(f'Task "{task}" loading error: {ex}\n')
                exit(-1)

            loader.exec_module(module)
            module.Command(self.root).run(args)
        else:
            sys.stderr.write(self.available_tasks_string())

    @classmethod
    def set_global_prepare_hook(cls, hook: Callable[[], None]):
        """
        Sets a global hook that runs before any task.

        This class method adds a function to the list of hooks that will be called
        before any task is executed.

        Parameters:
            hook (Callable[[], None]): A function to call before running any task.

        Example:
            CommandRunner.set_global_prepare_hook(lambda: print("Preparing to run a task..."))
        """
        cls.prepare_hooks.append(hook)

    @classmethod
    def _make_error_command_cls(cls, exception: Exception):
        """
        Creates a command class that represents an error.

        This private method is used internally to create a command class that represents
        an error that occurred while importing a task.

        Parameters:
            exception (Exception): The exception that occurred while importing the task.

        Returns:
            Type[CommandBase]: A command class that displays the error when run.
        """
        class ErrorCommand(CommandBase):
            help = terminal.colorize(f"IMPORT ERROR: {exception}", fg='red')

            def run(self, args):
                self.stdout.write(f"Command importing error!\n{traceback.format_exception(exception)}")
                exit(1)

        return ErrorCommand
