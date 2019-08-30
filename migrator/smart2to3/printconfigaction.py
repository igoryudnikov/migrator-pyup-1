import argparse
from shutil import copyfileobj
import sys


class PrintConfigAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs='?', **kwargs):
        #print(option_strings, dest, nargs, kwargs)
        if nargs != '?':
            raise ValueError("nargs should be '?', got: '{}'".format(nargs))
        super(PrintConfigAction, self).__init__(option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            values = sys.stdout
        copyfileobj(open(namespace.path_to_config), values)
        exit()
