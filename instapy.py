import imp
import threading


class Reloader(threading.Thread):
    def __init__(self, main_function, a=None, kwa=None, *args, **kwargs):
        self._n_reloads = 0
        self.args = a or tuple()
        self.kwargs = kwa or dict()
        self.main_function = main_function
        super(Reloader, self).__init__(*args, **kwargs)

    def run(self):
        self.main_function(*self.args, **self.kwargs)

    def get_module(self, import_str):
        self._n_reloads += 1
        return imp.load_module(import_str + str(self._n_reloads), *imp.find_module(import_str))
