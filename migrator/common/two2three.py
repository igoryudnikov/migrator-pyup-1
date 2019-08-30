import subprocess

from .utils import get_logger
from .async_utils import async_run
from ..common.utils import shorten

logger = get_logger()


class Two2Three:
    def __init__(self, executable='2to3'):
        self.executable = executable
        self.fixers = self._get_fixers()
        logger.debug('Available fixers are: %s', self.fixers)

    @staticmethod
    def _optimistic_run(*params):
        logger.debug('Running: %s', params)
        ps = subprocess.run(params, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if ps.returncode != 0:
            raise Exception('program {} finished with non-zero exit code: {}, '
                            'stderr: {}'.format(params[0], ps.returncode, ps.stderr))
        return ps.stdout.decode('utf-8')

    def _run(self, *params):
        params = [self.executable] + list(params)
        return self._optimistic_run(*params)

    def _get_fixers(self):
        return [x for x in self._run('-l').split('\n') if x
                and x == x.lower()]  # skip lines with description

    async def _run_async(self, *params):
        params = [self.executable] + list(params)
        command = ' '.join(params)

        out, err, exitcode = await async_run(command)

        if exitcode != 0:
            raise Exception('2to3 terminated with nonzero exit-code {} on file: {}, stderr: {}'
                            .format(exitcode, params[-1], shorten(err)))

        return out

    async def fix_async(self, path_to_project_or_file, write, fixers, params=tuple()):
        if write:
            params += ['-w', '-n']
        return await self._run_async(*params, *map(lambda f: '--fix=' + f, fixers),
                                     "'{}'".format(path_to_project_or_file))  # path can have spaces
