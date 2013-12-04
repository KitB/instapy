import sys

import log_config  # noqa

from instapy import execution


def main(*args):
    execution.gui_main(*args)

if __name__ == '__main__':
    main(*sys.argv[1:])
