import sys

import log_config  # noqa

from instapy import execution


def main(args):
    # We give a class as 'module.submodule.ClassName' and it'll run it. How
    # fancy!
    updater = execution.Updater(args)
    updater.run()

if __name__ == '__main__':
    main(sys.argv[1:])
