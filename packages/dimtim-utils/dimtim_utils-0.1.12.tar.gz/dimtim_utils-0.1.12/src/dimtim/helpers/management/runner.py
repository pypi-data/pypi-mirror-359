import os
import pkgutil
import sys
import traceback
from typing import Callable, Type

from dimtim.helpers.management import CommandBase
from dimtim.utils import importing, terminal


class CommandRunner:
    prepare_hooks: list[Callable[[], None]] = []

    def __init__(self, root: str, bin_path: str):
        self.root = os.path.normpath(root)
        self.os_path = os.path.normpath(os.path.join(self.root, bin_path))
        self.py_path = os.path.relpath(self.os_path, self.root).replace(os.sep, '.').strip('.')
        sys.path.append(self.root)

    def collect_tasks(self) -> list[tuple[str, Type[CommandBase]]]:
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
        return os.path.exists(os.path.join(self.os_path, f'{name}.py'))

    def run(self, *args: str):
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
        cls.prepare_hooks.append(hook)

    @classmethod
    def _make_error_command_cls(cls, exception: Exception):
        class ErrorCommand(CommandBase):
            help = terminal.colorize(f"IMPORT ERROR: {exception}", fg='red')

            def run(self, args):
                self.stdout.write(f"Command importing error!\n{traceback.format_exception(exception)}")
                exit(1)

        return ErrorCommand
