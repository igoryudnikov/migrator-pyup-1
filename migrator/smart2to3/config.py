from yaml import full_load

from ..common.utils import get_logger

logger = get_logger()


class Config:
    def __init__(self, path, _2to3):
        self._2to3 = _2to3
        self.config = full_load(open(path).read())
        logger.debug('Loaded configuration from %s: %s', path, self.config)

    def get_groups(self):
        return self.config['groups-{}'.format(self._2to3)]

    def get_all_fixers(self):
        return [fixer for group in self.get_groups() for fixer in group['fixers']]
