import getpass
import os
import sys
from abc import ABC
from argparse import ArgumentParser

from dimtim.helpers.management.command import CommandBase, CommandError


class CronCommand(CommandBase, ABC):
    comment = '...'
    schedule = '* * * * *'

    @staticmethod
    def _add_cron_arguments(parser: ArgumentParser):
        parser.add_argument('--setup', '-s', action='store_true', dest='setup', help='Setup cron task.')
        parser.add_argument('--remove', '-r', action='store_true', dest='remove', help='Remove cron task.')

    def run(self, args):
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
        cron = self.remove_task(partial=True)

        executable = os.path.join(os.path.dirname(sys.executable), 'dtrun')
        job = cron.new(command=f'cd {self.root} && {executable} {self.name}', comment=self.comment)
        job.setall(self.schedule)
        job.enable()
        cron.write()

        self.logger.debug(f'Taks "{self.name}" added to cron.')

    def remove_task(self, partial=False):
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
