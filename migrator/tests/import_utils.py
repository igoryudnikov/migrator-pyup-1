import unittest

from migrator.common.import_utils import *


class ImportUtilsSuite(unittest.TestCase):

    def test_get_import_lines_returns_empty_array_when_no_matches_found(self):
        actual_result = get_import_lines('data/import_utils/before.example', '__future__')
        expected_result = []
        self.assertEqual(expected_result, actual_result)

    def test_get_import_lines_returns_all_matching_lines(self):
        actual_result = get_import_lines('data/import_utils/after.example', '__future__')
        expected_result = ['from __future__ import print_function', 'from __future__ import division, with_statement']
        self.assertEqual(expected_result, actual_result)

    def test_to_single_line_groups_all_import_to_single_line(self):
        actual_result = to_single_line(get_import_lines('data/import_utils/after.example', '__future__'), '__future__')
        expected_result = 'from __future__ import print_function, division, with_statement'
        self.assertEqual(expected_result, actual_result)

    def test_remove_lines_from_file(self):
        file_name = 'data/import_utils/remove_lines.txt'
        original_data = ['foo', 'bar', 'baz', 'fuzz', 'nike']
        lines_to_remove = ['bar', 'fuzz']

        write_lines(file_name, original_data, 'w+')

        remove_lines_from_file(file_name, lines_to_remove)

        expected_result = ['foo', 'baz', 'nike']
        actual_result = read_lines(file_name)

        self.assertEqual(expected_result, actual_result)

    def test_prepend_line(self):
        file_name = 'data/import_utils/prepend_lines.txt'
        original_data = ['foo', 'bar', 'baz']
        lines_to_add = ['fuzz', 'nike']

        write_lines(file_name, original_data, 'w+')
        prepend_lines_into_file(file_name, lines_to_add)

        actual_result = read_lines(file_name)
        expected_result = ['fuzz', 'nike', 'foo', 'bar', 'baz']

        self.assertEqual(expected_result, actual_result)


if __name__ == '__main__':
    unittest.main()