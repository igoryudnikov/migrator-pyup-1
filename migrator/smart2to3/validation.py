from ..common.utils import shorten


def require_nothing_to_commit(repo):
    if repo.has_changes():
        msg = shorten('Repository must not have untracked/uncommitted/changed files: '
                      '{}/{}/{}'.format(repo.get_untracked_files(),
                                        repo.get_uncommitted_files(),
                                        repo.get_changed_files()))
        raise Exception(msg)


def require_all_fixers_are_available(config, two2three):
    required = set(config.get_all_fixers())
    available = set(two2three.fixers)

    if required.intersection(available) != required:
        raise Exception('Some fixers are not available: {}'.format(required.difference(available)))
