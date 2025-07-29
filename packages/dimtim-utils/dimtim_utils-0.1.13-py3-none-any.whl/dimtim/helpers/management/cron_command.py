import getpass
import os
import sys
from abc import ABC
from argparse import ArgumentParser

from dimtim.helpers.management.command import CommandBase, CommandError


class CronCommand(CommandBase, ABC):
    """
    A base class for defining tasks that can be scheduled with cron.

    This class extends CommandBase to provide functionality for adding, removing,
    and managing cron jobs. Subclasses should define the `comment` and `schedule`
    attributes, and implement the `handle` method.

    Attributes:
        comment (str): A comment to identify the cron job.
        schedule (str): The cron schedule expression (default: '* * * * *').

    Example:
        from dimtim.helpers.management.cron_command import CronCommand
        from argparse import ArgumentParser

        class Command(CronCommand):
            help = 'A sample cron task that runs daily'
            comment = 'Daily greeting task'
            schedule = '0 0 * * *'  # Run at midnight every day

            def add_arguments(self, parser: ArgumentParser):
                parser.add_argument('--name', '-n', default='World', help='Name to greet')

            def handle(self, **kwargs):
                name = kwargs.get('name', 'World')
                self.stdout.write(f"Hello, {name}!")
    """
    comment = '...'
    schedule = '* * * * *'

    @staticmethod
    def _add_cron_arguments(parser: ArgumentParser):
        """
        Adds cron-specific arguments to the argument parser.

        Parameters:
            parser (ArgumentParser): The argument parser to add arguments to.
        """
        parser.add_argument('--setup', '-s', action='store_true', dest='setup', help='Setup cron task.')
        parser.add_argument('--remove', '-r', action='store_true', dest='remove', help='Remove cron task.')

    def run(self, args):
        """
        Runs the command with the given arguments.

        This method parses the command-line arguments and either sets up a cron task,
        removes a cron task, or runs the command's handle method.

        Parameters:
            args (list): The command-line arguments.

        Raises:
            CommandError: If an error occurs during command execution.
        """
        parser = ArgumentParser(description=self.help)
        self._add_cron_arguments(parser)
        self.add_arguments(parser)
        args = vars(parser.parse_args(args))
        try:
            if args.pop('setup', False):
                return self.setup_task()
            if args.pop('remove', False):
                return self.remove_task()
            self.handle(**args)
        except CommandError as e:
            sys.stderr.write(str(e))

    def setup_task(self):
        """
        Add the task to the user's crontab.

        This method creates a new cron job with the specified schedule and adds it
        to the user's crontab. If a job with the same comment already exists, it is
        removed first.

        Returns:
            None

        Raises:
            ModuleNotFoundError: If the python-crontab library is not installed.
        """
        cron = self.remove_task(partial=True)

        executable = os.path.join(os.path.dirname(sys.executable), 'dtrun')
        job = cron.new(command=f'cd {self.root} && {executable} {self.name}', comment=self.comment)
        job.setall(self.schedule)
        job.enable()
        cron.write()

        self.logger.debug(f'Taks "{self.name}" added to cron.')

    def remove_task(self, partial=False):
        """
        Remove the task from the user's crontab.

        This method removes any cron jobs with the specified comment from the user's crontab.

        Parameters:
            partial (bool): If True, returns the CronTab object without writing changes.
                           This is used internally by setup_task. Default is False.

        Returns:
            CronTab or None: If partial is True, returns the CronTab object.
                            Otherwise, returns None.

        Raises:
            ModuleNotFoundError: If the python-crontab library is not installed.
        """
        try:
            from crontab import CronTab
        except ImportError:
            raise ModuleNotFoundError('For use the crontab commands, you need to install the "python-crontab" library')

        cron = CronTab(user=getpass.getuser())
        for job in cron.find_comment(self.comment):
            cron.remove(job)

        if partial:
            return cron

        cron.write()
        self.logger.debug(f'Taks "{self.name}" removed from cron.')
