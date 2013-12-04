import importlib

from instapy import reloader
from instapy import server


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
        self.reloader = reloader.Reloader(looper)

        self.server = server.Server(self.reloader)

    def run(self):
        self.reloader.start()
        self.server.start()

        try:
            self.reloader.join()
        except KeyboardInterrupt:
            self.reloader.running = False
            self.reloader.join()
