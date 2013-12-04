import sys

import log_config  # noqa

from instapy import execution

main = execution.main

if __name__ == '__main__':
    main(*sys.argv[1:])
