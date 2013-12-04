import sys

import log_config  # noqa

from instapy import execution


def main(game_instance_string):
    # We give a class as 'module.submodule.ClassName' and it'll run it. How
    # fancy!
    execution.main(game_instance_string)

if __name__ == '__main__':
    main(*sys.argv[1:])
