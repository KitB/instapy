import importlib
import sys

from watchdog import observers

from instapy import gui
from instapy import reloader
from instapy import watcher


def get_looper(looper_string):
    (module_name, dot, cls_name) = looper_string.rpartition('.')
    # This will probably break on Windows machines.
    module_name = '.'.join(module_name.split('/'))
    module = importlib.import_module(module_name)
    cls = module.__dict__[cls_name]
    return cls()


class Updater(object):
    def __init__(self, args):
        looper = get_looper(args[0])
        r = reloader.Reloader(looper)
        handler = watcher.Notifier(r)
        o = observers.Observer()
        o.schedule(handler, path='.', recursive=True)

        self.looper = looper
        self.reloader = r
        self.watcher = handler
        self.observer = o

    def run(self):
        self.observer.start()
        self.reloader.start()
        try:
            gui.main(sys.argv, self.watcher)
        except KeyboardInterrupt:
            pass
        finally:
            self.reloader.running = False
            self.observer.stop()
            self.observer.join()
            self.reloader.join()
