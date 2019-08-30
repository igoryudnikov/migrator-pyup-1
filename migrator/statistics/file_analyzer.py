from collections import defaultdict

from .abstract_analyzer import SingleFileAbstractAnalyzer


class FileAnalyzer(SingleFileAbstractAnalyzer):
    async def analyze(self, path_to_file):
        return len(open(path_to_file, 'rt').readlines())

    def extract_useful(self, lines_count):
        return [lines_count]

    @staticmethod
    def possible_keys():
        return ['files', 'lines']

    def collect_stats(self, useful_iterator):
        result = defaultdict(int)
        for count in useful_iterator:
            result['files'] = 1
            result['lines'] += count
        return dict(result)
