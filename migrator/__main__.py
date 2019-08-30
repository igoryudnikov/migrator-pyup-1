import argparse
from os.path import expanduser

from .smart2to3 import register as reg_2to3, run as run_2to3
from .statistics import register as reg_stats, run as run_stats
from .common.utils import activate_logging, get_logger


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--log-level', default='WARN', type=lambda s: s.upper(),
                        choices=['NONE', 'DEBUG', 'INFO', 'WARN', 'ERROR'],
                        help='Log-level for stderr, default: WARN')
    parser.add_argument('--full-log-path', default=expanduser('~/.migrator_full_log'),
                        help='file to store full logs. Use /dev/null if you don\'t want to store them. '
                             'Default: ~/.migrator_full_log')

    subparsers = parser.add_subparsers()
    subparsers.required = True
    subparsers.dest = 'command'

    sub_projects = {
        'smart2to3': (reg_2to3, run_2to3),
        'statistics': (reg_stats, run_stats)
    }

    for name, (reg_foo, _) in sub_projects.items():
        sub_parser = subparsers.add_parser(name)
        reg_foo(sub_parser)
        sub_parser.set_defaults(migrator_choise=name)

    args = parser.parse_args()
    activate_logging(args.log_level, args.full_log_path)
    logger = get_logger()
    logger.debug('Parsed args: %s', args)

    sub_projects[args.migrator_choise][1](args)
