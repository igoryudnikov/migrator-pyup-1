from abc import ABC, abstractmethod


class SingleFileAbstractAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, path_to_file):
        """
        :return: return analyzers output, usually too verbose
        """
        pass

    @abstractmethod
    def extract_useful(self, log):
        """
        :return: iterable of extracted succinct useful info from log, i.e. warnings with positions in file
        """
        pass

    @staticmethod
    @abstractmethod
    def possible_keys():
        """
        :return: list of all possible keys from `collect_stats` result
        """
        pass

    @abstractmethod
    def collect_stats(self, useful_iterator):
        """
        :param useful_iterator: iterator, returned from `extract_useful`
        :return: dict with statistics
        """
        pass
