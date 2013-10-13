import importlib
import sys
import time

import log_config

from instapy import reloader
from instapy import watcher
from watchdog import observers


def get_looper(looper_string):
    (module_name, dot, cls_name) = looper_string.rpartition('.')
    # This will probably break on Windows machines.
    module_name = '.'.join(module_name.split('/'))
    module = importlib.import_module(module_name)
    cls = module.__dict__[cls_name]
    return cls()


def main(args):
    # We give a class as 'module.submodule.ClassName' and it'll run it. How
    # fancy!
    looper = get_looper(args[0])
    r = reloader.Reloader(looper)
    handler = watcher.Notifier(r)
    o = observers.Observer()
    o.schedule(handler, path='.', recursive=True)
    o.start()
    r.start()
    try:
        while True:
            if not r.is_alive():
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        r.running = False
        o.stop()
        o.join()
        r.join()

if __name__ == '__main__':
    main(sys.argv[1:])
