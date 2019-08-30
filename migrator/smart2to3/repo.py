import os
import git

from ..common.utils import get_logger

logger = get_logger()


class Repo:
    def __init__(self, path):
        self.repo = git.Repo(path)

    def has_changes(self):
        return bool(self.get_untracked_files()) or bool(self.get_uncommitted_files()) or bool(self.get_changed_files())

    def get_untracked_files(self):
        return self.repo.untracked_files

    def get_uncommitted_files(self):
        return [item.a_path for item in self.repo.index.diff('HEAD')]

    def get_changed_files(self):
        return [item.a_path for item in self.repo.index.diff(None)]

    def add(self, pattern='--all'):
        logger.debug('adding: %s, untracked: %s', pattern, self.get_untracked_files())
        self.repo.git.add(pattern)

    def commit(self, msg, description=None):
        if description is not None:
            msg += (os.linesep * 2) + description

        logger.debug('comitting with message: "%s", uncommited: "%s", changed: "%s", untracked: "%s"',
                     msg, self.get_uncommitted_files(), self.get_changed_files(), self.get_untracked_files())
        self.repo.index.commit(msg)

    def get_commits(self):
        return list(self.repo.iter_commits())
