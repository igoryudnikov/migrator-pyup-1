import argparse
import asyncio
import multiprocessing
import os

from tqdm import tqdm

from ..common.import_utils import *
from .config import Config
from .printconfigaction import PrintConfigAction
from .repo import Repo
from .validation import *
from ..common.two2three import Two2Three
from ..common.utils import locate_resource, get_dir_path, get_logger, list_files

from typing import List, Dict

logger = get_logger()


def register(parser):
    parser.add_argument('--write', action='store_true', help='without this flag NO changes will be made to project '
                                                             '(but you can check params and get some info)')
    parser.add_argument('-f', '--path-to-config', help='file with config (if skipped, will use default)',
                        default=locate_resource('default-groups.yaml'))
    parser.add_argument('--export-config', metavar='PATH', action=PrintConfigAction, type=argparse.FileType('w'),
                        help='Print configuration file and exit. Optional `PATH` parameter can be used to '
                             'save exported data into specific file.', nargs='?')
    parser.add_argument('path_to_project', help='path to local directory with project, must be tracked with git '
                                                'and not have any uncommitted changes', type=get_dir_path)
    extensions_default = ('.py', '.py3', '.pyw')
    parser.add_argument('--python-extensions', default=extensions_default, nargs='+',
                        help='list of python file extensions, default: "{}"'.format(' '.join(extensions_default)))
    parser.add_argument('--parallelism-level', help='level of parallelism, default: min(8, cpu_count)',
                        default=min(8, multiprocessing.cpu_count()))
    parser.add_argument('--futurize', action='store_true', help='flag to use futurize instead of 2to3')


async def _run_with_progress_bar_async(tasks, pb_position=0):
    total_result = {}
    errors = []
    tasks_bar = tqdm(asyncio.as_completed(tasks), total=len(tasks), unit='f', position=pb_position, leave=None)

    for x in tasks_bar:
        try:
            rel_path, result = await x
            total_result[rel_path] = result
            tasks_bar.set_description(rel_path)
        except Exception as e:
            errors.append(e)

    tasks_bar.clear()
    return total_result, errors


def run(args):
    executable_2to3 = 'futurize' if args.futurize else '2to3'
    configuration = Config(args.path_to_config, executable_2to3)
    repository = Repo(args.path_to_project)
    two_2_three = Two2Three(executable_2to3)

    # basic validation
    require_all_fixers_are_available(configuration, two_2_three)
    require_nothing_to_commit(repository)

    loop = asyncio.get_event_loop()
    sem = asyncio.Semaphore(args.parallelism_level)

    imports_before = {}
    imports_after = {}

    async def file_to_result_async(full_path, path_to_project):
        rel_path = os.path.relpath(full_path, path_to_project)

        imports = get_import_lines(full_path, '__future__')
        if imports and full_path not in imports_before:
            imports_before[full_path] = imports
        elif imports:
            raise Exception('not expected case, handle it')

        async with sem:
            params = group.get('params')
            if params is None:
                params = []

            if args.write:
                write_params = group.get('only_on_write_params')
                if write_params is not None:
                    params.extend(write_params)

            result = await two_2_three.fix_async(full_path, args.write, group['fixers'], params)
        return rel_path, result

    def remember_and_remove_added_future_imports(files: List[str]):
        for f in files:
            maybe_before = imports_before.get(f)
            set_before = set()
            if maybe_before:
                set_before = set(maybe_before)

            imports = list(set(get_import_lines(f, '__future__')) - set_before)

            if imports and f not in imports:
                imports_after[f] = imports
                remove_lines_from_file(f, imports)
            elif imports:
                current_value = imports[f]
                imports_after[f] = current_value.join(imports)
                remove_lines_from_file(f, imports)

    meta = {'commits_cnt': 0}
    groups_bar = tqdm(configuration.get_groups(), position=0, unit='group')
    groups_bar.set_postfix(meta)
    for group in groups_bar:
        groups_bar.set_description('group: "{}"'.format(group['name']))

        tasks = []
        for file in list_files(args.path_to_project, extensions=args.python_extensions):
            tasks.append(file_to_result_async(file, args.path_to_project))

        changes, errors = loop.run_until_complete(_run_with_progress_bar_async(tasks, 1))

        logger.debug('group: %s, fixers %s, changes: %s, errors: %s',
                     group['name'], group['fixers'], changes, errors)

        if errors:
            logger.warning('Group "%s" completed with %s errors: \n%s', group['name'], len(errors),
                           '\n'.join(map(lambda e: '- ' + ' '.join(e.args), errors)))

        if args.write and repository.has_changes():
            repository.add()  # do we need it?
            remember_and_remove_added_future_imports(list_files(args.path_to_project, extensions=args.python_extensions))
            repository.commit('[smart2to3] {}'.format(group['name']), group.get('description'))
            meta['commits_cnt'] += 1

        groups_bar.set_description_str('')
        groups_bar.set_postfix(meta)

    if args.write and imports_after:
        for (k, v) in imports_after.items():
            prepend_lines_into_file(k, v)

    if repository.has_changes():
        repository.add()
        repository.commit('[smart2to3] __future__ imports', '__future__ imports')

    loop.close()
