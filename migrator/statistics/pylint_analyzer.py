from collections import defaultdict
import sys
import json

from .abstract_analyzer import SingleFileAbstractAnalyzer
from ..common.two2three import Two2Three
from ..common.utils import get_logger, shorten
from ..common.async_utils import async_run

logger = get_logger()


class PyLintAnalyzer(SingleFileAbstractAnalyzer, Two2Three):
    async def analyze(self, path_to_file):
        stdout, stderr, _ = await async_run(
            '{} -m pylint --py3k --persistent=n --score=n --output-format=json'
            ' --disable=no-absolute-import {}'.format(sys.executable, path_to_file)
        )

        if stderr:
            raise Exception('pylint has non-empty stderr: {}'.format(shorten(stderr)))

        return stdout

    def extract_useful(self, log):
        return json.loads(log)

    @staticmethod
    def possible_keys():
        return ['error', 'warning', 'refactor', 'convention']

    def collect_stats(self, useful_iterator):
        result = defaultdict(int)
        for message in useful_iterator:
            result[message['type']] += 1
        return dict(result)
