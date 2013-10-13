import importlib
import sys
import time

from instapy import reloader
from instapy import watcher
from watchdog import observers


def get_looper(looper_string):
    (module_name, dot, cls_name) = looper_string.rpartition('.')
    module = importlib.import_module(module_name)
    cls = module.__dict__[cls_name]
    return cls()


if __name__ == "__main__":
    # We give a class as 'module.submodule.ClassName' and it'll run it. How
    # fancy!
    looper = get_looper(sys.argv[1])
    r = reloader.LooperReloader(looper)
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
