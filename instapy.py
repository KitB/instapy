import imp
import threading
import sys
import inspect
import types
import collections
import re


class CachedReloader(object):
    def __init__(self):
        self._n_reloads = 0
        self._d = dict()

    def new_generation(self):
        del self._d
        self._d = dict()

    def get_module(self, str_or_module):
        if isinstance(str_or_module, basestring):
            try:
                return self._d[str_or_module]
            except KeyError:
                m = self._load_module(str_or_module)
                self._d[str_or_module] = m
                return m
        elif isinstance(str_or_module, types.ModuleType):
            return self.get_module(self._get_module_name(str_or_module))

    def _load_module(self, import_str):
        self._n_reloads += 1
        suffix = "_reloaded_%d_times" % self._n_reloads
        return imp.load_module(import_str + suffix, *imp.find_module(import_str))

    def _get_module_name(self, module):
        suffix_re = re.compile("^(.*)_reloaded_[0-9]+_times$")
        m = suffix_re.match(module.__name__)
        if m:
            return m.group(1)
        else:
            return module.__name__


class Reloader(threading.Thread):
    def __init__(self, main_function, init_function, init_once=None, *args, **kwargs):
        super(Reloader, self).__init__(*args, **kwargs)
        self._n_reloads = 0
        self.main_function = main_function
        self.init_function = init_function
        self.init_once = init_once
        self.daemon = True
        self.updated = False
        self.running = False
        self._cached_reloader = CachedReloader()

    def _loop(self):
        while self.running:
            if self.updated:
                self._do_update()
                self.updated = False
            self.main_function(*(self.init_args + self.args))

    def run(self):
        self.running = True
        if self.init_once:
            self.init_args = self.init_once()
        else:
            self.init_args = ()
        self.args = self.init_function()
        self._loop()
        print "Thread exit"

    def _do_update(self):
        print "Updating"
        # Tell the reloader to flush its cache
        self._cached_reloader.new_generation()

        # Reload the main function
        m = reload(inspect.getmodule(self.main_function))
        self.main_function = m.__getattribute__(self.main_function.__name__)

        # Reload the initialisation arguments
        n = reload(inspect.getmodule(self.init_function))
        self.init_function = n.__getattribute__(self.init_function.__name__)
        self.args = self.init_function()

        # Reload the rest
        for k, v in self.main_function.func_globals.items():
            if k != "__builtins__":
                if isinstance(v, types.ModuleType):
                    if not v.__name__.startswith("pygame"):
                        self.main_function.func_globals[k] = self._cached_reloader.get_module(v)
                elif isinstance(v, types.FunctionType):
                    m = self._cached_reloader.get_module(inspect.getmodule(v))
                    new_v = m.__getattribute__(v.__name__)
                    self.main_function.func_globals[k] = new_v

    def update(self):
        self.updated = True
