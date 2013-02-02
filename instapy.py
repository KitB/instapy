import imp
import threading
import sys
import inspect
import types


class Reloader(threading.Thread):
    def __init__(self, main_function, a=None, kwa=None, *args, **kwargs):
        super(Reloader, self).__init__(*args, **kwargs)
        self._n_reloads = 0
        self.args = a or tuple()
        self.kwargs = kwa or dict()
        self.main_function = main_function
        self.daemon = True
        self.updated = False
        self.running = False

    def _loop(self):
        while self.running:
            if self.updated:
                self._do_update()
                self.updated = False
            self.main_function(*self.args, **self.kwargs)
        print "Thread exit"

    def run(self):
        self.running = True
        self._loop()

    def _do_update(self):
        for k, v in self.main_function.func_globals.items():
            if k != "__builtins__":
                if isinstance(v, types.ModuleType):
                    self.main_function.func_globals[k] = reload(v)

    def update(self):
        self.updated = True

    def get_module(self, import_str):
        self._n_reloads += 1
        return imp.load_module(import_str + str(self._n_reloads), *imp.find_module(import_str))
