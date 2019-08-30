import argparse

from . import register, run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    register(parser)
    run(parser.parse_args())
