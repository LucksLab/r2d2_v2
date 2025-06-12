
import sys

from .src import R2D2


def _usage():
    print('Usage:  python3 -m r2d2_v2 [config_path] [base_path]')
    print('             defaults: ')
    print('                 config_path = ./r2d2.json')
    print('                 base_path = .')


def main():
    bp = None
    cp = None
    if len(sys.argv) > 3:
        _usage()
        sys.exit(-1)
    if len(sys.argv) > 2:
        cp = sys.argv[2]
    if len(sys.argv) > 1:
        bp = sys.argv[1]

    R2D2(base_path=bp, config_path=cp, run_now=True)
