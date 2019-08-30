import json
import csv
from collections import OrderedDict


class ResultPrinter:
    def __init__(self, file, format, analyzers):
        self.file = file
        if format == 'jsonl':
            self.output = self.__json_output
        elif format == 'csv' or format == 'csv-no-header':
            self.output = self.__csv_output

            fieldnames = ['name'] + ["{}.{}".format(name, key)
                          for name, analyzer in analyzers.items()
                          for key in analyzer.possible_keys()]

            self.__csv_writer = csv.DictWriter(file, fieldnames)
            if format != 'csv-no-header':
                self.__csv_writer.writeheader()
        else:
            raise Exception('unknown format: {}'.format(format))

    def __csv_output(self, filename, statistics):
        result = {
            "{}.{}".format(name, key): value
            for name, stats in statistics.items()
            for key, value in stats.items()
        }
        result['name'] = filename
        self.__csv_writer.writerow(result)

    def __json_output(self, filename, statistics):
        print(json.dumps(OrderedDict([
            # with OrderedDict this order will be preserved in output json (for readability)
            ('name', filename),
            ('result', statistics)
        ])), file=self.file)
