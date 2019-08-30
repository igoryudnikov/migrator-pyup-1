import re
from .utils import read_lines, write_lines


def get_import_lines(file_name, package):
    file = read_lines(file_name)
    acc = []
    head = 'from ' + package + ' import'

    for l in file:
        if re.match('^' + head + '.*', l) is not None:
            acc.append(l.strip())

    return acc


def to_single_line(lines, package):
    tokens = []
    head = 'from ' + package + ' import '

    for l in lines:
        if re.match('^' + head + '.*', l) is None:
            raise Exception('')

        for t in l.replace(head, '').split(','):
            strip = t.strip()
            if strip != '':
                tokens.append(strip)

    return head + ', '.join(tokens)


def remove_lines_from_file(file_name, lines):
    data = read_lines(file_name)

    candidate_lines = []

    for l in data:
        if l not in lines:
            candidate_lines.append(l)
        else:
            l

    file = open(file_name, 'w')
    file.flush()
    file.write('\n'.join(candidate_lines))
    file.close()


def prepend_lines_into_file(file_name, lines_to_prepend):
    lines = read_lines(file_name)
    candidate = []
    for l in lines_to_prepend:
        candidate.append(l)

    for l in lines:
        candidate.append(l)

    write_lines(file_name, candidate)
