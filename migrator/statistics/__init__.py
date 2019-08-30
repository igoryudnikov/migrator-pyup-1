from ..common.utils import list_files
from .pylint_analyzer import PyLintAnalyzer
from .two2three_analyzer import Two2ThreeAnalyzer
from .file_analyzer import FileAnalyzer
from ..common.utils import get_logger, get_dir_path
import argparse
from tqdm import tqdm
import os
import asyncio
import multiprocessing
from collections import defaultdict
from .result_printer import ResultPrinter

logger = get_logger()


def register(parser):
    analyzers = ['2to3', 'pylint', 'file']

    parser.add_argument('--2to3', help='2to3 executable, default: 2to3', default='2to3')
    parser.add_argument('path_to_project', help='path to local directory with project, must be tracked with git '
                                                'and not have any uncommitted changes', type=get_dir_path)
    parser.add_argument('--full', help='full, per-file statistics, default: false', action='store_true')
    parser.add_argument('--disable', nargs='+', help='manually disable analyzers: %s' % analyzers,
                        choices=analyzers, default=[])
    format_choices = ['jsonl', 'csv', 'csv-no-header']
    default_format = format_choices[0]  # the first one is default
    parser.add_argument('--format', choices=format_choices, default=default_format, type=lambda x: x.lower(),
                        help='Output format, default: {}'.format(default_format))
    parser.add_argument('-o', '--output', help='file to output. If omitted, output goes to stdout',
                        type=argparse.FileType('w'), default='-')
    parser.add_argument('--parallelism-level', help='level of parallelism, default: min(8, cpu_count)',
                        default=min(8, multiprocessing.cpu_count()))
    ignore_defaults = ['venv/', 'build/']
    parser.add_argument('--ignore', help='list of ignored file-prefixes. File will be ignored if its path from '
                                         'path_to_project starts with one of this. '
                                         'Default: "{}"'.format(' '.join(ignore_defaults)),
                                         nargs='+',
                                         default=ignore_defaults)


def run(args):
    _2to3 = args.__dict__['2to3']  # yeah, it's ugly

    analyzer_to_constructor = {
        '2to3': lambda: Two2ThreeAnalyzer(_2to3),
        'futurize': lambda: Two2ThreeAnalyzer('futurize'),
        'pylint': lambda: PyLintAnalyzer(),
        'file': lambda: FileAnalyzer()
    }

    analyzers = {k: v() for k, v in analyzer_to_constructor.items() if k not in args.disable}

    files = list_files(args.path_to_project, ignored_prefixes=args.ignore,
                       extensions=('.py', '.py3', '.pyw'))  # TODO parametrize or delete

    sem = asyncio.Semaphore(args.parallelism_level)

    async def count_all_on_file(full_path, rel_path):
        result = {}
        for name, analyzer in analyzers.items():
            try:
                async with sem:
                    log = await analyzer.analyze(full_path)
                useful_iterator = analyzer.extract_useful(log)
                stats = analyzer.collect_stats(useful_iterator)

                result[name] = stats
            except Exception as e:
                logger.warning('analyzer "%s" on file "%s" raised error: %s', name, rel_path, e)
        return rel_path, result

    tasks = []
    for full_path in files:
        rel_path = os.path.relpath(full_path, args.path_to_project)
        tasks.append(count_all_on_file(full_path, rel_path))

    printer = ResultPrinter(args.output, args.format, analyzers)

    async def run_with_progress_bar(tasks):
        total_statistics = defaultdict(lambda: defaultdict(int))

        tasks_bar = tqdm(asyncio.as_completed(tasks), total=len(tasks), unit='f')
        for x in tasks_bar:
            rel_path, result = await x
            if args.full:
                tasks_bar.clear()
                printer.output(rel_path, result)
            tasks_bar.set_description('done {}'.format(rel_path))

            for analyzer_name, analyzer_result in result.items():
                for k, v in analyzer_result.items():
                    total_statistics[analyzer_name][k] += v

        return total_statistics

    loop = asyncio.get_event_loop()
    total_statistics = loop.run_until_complete(run_with_progress_bar(tasks))
    printer.output(':total:', total_statistics)
    loop.close()
