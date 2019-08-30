from collections import defaultdict

from .abstract_analyzer import SingleFileAbstractAnalyzer
from ..common.two2three import Two2Three
from ..common.utils import get_logger

logger = get_logger()


class Two2ThreeAnalyzer(SingleFileAbstractAnalyzer, Two2Three):
    async def analyze(self, path_to_file):
        return await self.fix_async(path_to_file, write=False, fixers=self.fixers)

    def extract_useful(self, log):
        def is_useful_line(line):
            line = line.strip()
            if not line or line.startswith('+++') or line.startswith('---'):
                return False
            elif line.startswith('+') or line.startswith('-'):
                return True

        return filter(is_useful_line, log.split('\n'))

    @staticmethod
    def possible_keys():
        return ['added', 'removed']

    def collect_stats(self, useful_iterator):
        result = defaultdict(int)
        for line in useful_iterator:
            result['added' if line[0] == '+' else 'removed'] += 1
        return dict(result)
