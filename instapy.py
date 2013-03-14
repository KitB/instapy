import imp
import threading
import sys
import inspect
import types
import collections
import re
import traceback
import time


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

class Looper(object):
    """ Mostly unnecessary at the moment
        Provides default methods, gives future potential for modifying class
        behaviours """
    def init_once(self):
        pass

    def init(self):
        pass

    def loop_body(self):
        pass


class LooperReloader(threading.Thread):
    def __init__(self, looper, *args, **kwargs):
        super(LooperReloader, self).__init__(*args, **kwargs)
        self._n_reloads = 0
        self.daemon = True
        self.updated = False
        self.running = False
        self.looper = looper
        self._cached_reloader = CachedReloader()

    def update(self):
        self.updated = True

    def run(self):
        self.running = True
        self.looper.init_once()
        self.looper.init()
        self._loop()
        print "Thread exit"

    def _do_update(self):
        print "Updating"
        # Tell the reloader to flush its cache
        self._cached_reloader.new_generation()

        # Reload the looper class
        m = reload(inspect.getmodule(self.looper))
        lc = m.__getattribute__(self.looper.__class__.__name__)
        lc_instance = lc()
        old_lc_instance = self.looper.__class__()

        # Reload the main function
        self.looper.loop_body = lc.loop_body.__get__(self.looper, lc)

        # Reload the initialisation arguments
        lc_instance.init()
        old_lc_instance.init()
        for name, value in vars(lc_instance).items():
            if inspect.isroutine(value):
                try:
                    if inspect.getsource(value) != inspect.getsource(vars(old_lc_instance)[name]):
                        self.looper.__dict__[name] = value
                except KeyError:
                    # New function
                    print "KeyError"
                    self.looper.__dict__[name] = value
            else:
                try:
                    if value != vars(old_lc_instance)[name]:
                        print name + " " + str(value) + ", " + str(vars(old_lc_instance)[name])
                        self.looper.__dict__[name] = value
                except KeyError:
                    # The property is a new one
                    print "property KeyError"
                    self.looper.__dict__[name] = value
        self.looper.__class__ = lc

        # Reload the rest
        for k, v in self.looper.loop_body.func_globals.items():
            if k != "__builtins__":
                if isinstance(v, types.ModuleType):
                    if not v.__name__.startswith("pygame"):
                        self.looper.loop_body.func_globals[k] = self._cached_reloader.get_module(v)
                elif isinstance(v, types.FunctionType):
                    m = self._cached_reloader.get_module(inspect.getmodule(v))
                    new_v = m.__getattribute__(v.__name__)
                    self.looper.loop_body.func_globals[k] = new_v

    def _loop(self):
        while self.running:
            try:
                if self.updated:
                    self.updated = False
                    self._do_update()
                if self.looper.loop_body():
                    self.running = False
            except Exception, e:
                traceback.print_exc()
                time.sleep(5)
