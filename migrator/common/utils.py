import logging
import os
import sys
from typing import List

def get_logger():
    return logging.getLogger('migrator')


def activate_logging(stderr_level, full_log_file_path):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    root = get_logger()
    root.setLevel(logging.DEBUG)

    full_log = logging.FileHandler(full_log_file_path, mode='w')
    full_log.setLevel(logging.DEBUG)
    full_log.setFormatter(formatter)
    root.addHandler(full_log)

    if stderr_level != 'NONE':
        stderr_log = logging.StreamHandler(sys.stderr)
        stderr_log.setLevel(stderr_level)
        stderr_log.setFormatter(formatter)
        root.addHandler(stderr_log)


def shorten(s, limit=1000):
    if len(s) <= limit:
        return s
    else:
        return s[:limit] + ' ... ({} chars more)'.format(len(s) - limit)


def get_dir_path(string):
    string = os.path.abspath(string)
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def locate_resource(path):
    return os.path.join(os.path.dirname(__file__), 'resources', path)


def list_files(path, *,
               extensions=('',),  # that means any
               ignored_prefixes=tuple()):
    py_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if any(file.endswith(e) for e in extensions):
                filename = os.path.abspath(os.path.join(root, file))
                rel_path = os.path.relpath(filename, path)
                if not any(rel_path.startswith(p) for p in ignored_prefixes):
                    py_files.append(filename)
    return py_files


def write_lines(file_name, lines, mode='w', is_critical=False):
    try:
        file = open(file_name, mode)
        file.flush()
        file.write('\n'.join(lines))
        file.close()
    except Exception as e:
        txt = "can't write " + str(len(lines)) + " into file " + file_name
        logging.error(txt)
        if is_critical:
            raise e


def read_lines(file_name) -> List[str]:
    try:
        file = open(file_name, 'r')
        lines = file.read().split('\n')
        file.close()
        return lines
    except Exception as e:
        txt = "can't read from file " + file_name
        logging.error(txt)
        raise e
