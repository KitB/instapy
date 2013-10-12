import imp
import inspect
import ipdb
import logging
import threading
import time
import traceback
import types


def load_module(fqname):
    """Return an imported module without filling sys.modules."""
    name, path = get_dotted_path(fqname)

    try:
        (module_file, p, description) = imp.find_module(name, [path])
    except ImportError:
        (module_file, p, description) = imp.find_module(name)

    if module_file is None:
        if description[2] == imp.C_BUILTIN:
            return imp.init_builtin(fqname)
        # Module was a package, we need to get __init__.py for that package
        (module_file, p, description) = imp.find_module('__init__', [p])

    module = imp.new_module(fqname)
    module.__file__ = module_file.name
    exec module_file in module.__dict__

    return module


def get_dotted_path(name):
    parts = name.split('.')
    head = parts[-1]
    tail = parts[:-1]

    path = '/'.join(tail)

    return head, path


class CachedReloader(object):
    """Provides a cached import mechanism.

       Allows the programmer to reset this cache between "generations"
    """
    def __init__(self):
        self._modules = dict()

    def new_generation(self):
        """Reset the cache."""
        del self._modules
        self._modules = dict()

    def get_module(self, str_or_module):
        """Either import and return a module or get it from the dictionary."""
        if isinstance(str_or_module, basestring):
            try:
                return self._modules[str_or_module]
            except KeyError:
                module = load_module(str_or_module)
                self._modules[str_or_module] = module
                return module
        elif isinstance(str_or_module, types.ModuleType):
            return self.get_module(str_or_module.__name__)


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


class Reloader(threading.Thread):
    def __init__(self, looper, debug_on_exception=True, *args, **kwargs):
        super(Reloader, self).__init__(*args, **kwargs)
        self.daemon = True
        self.updated = False
        self.running = False
        self.looper = looper
        self.debug_on_exception = debug_on_exception
        self._cached_reloader = CachedReloader()

    def update(self):
        self.updated = True

    def run(self):
        self.running = True
        self.looper.init_once()
        self.looper.init()
        self._loop()
        logging.info("Thread exit")

    def _do_update(self):
        logging.debug("Updating")
        # Tell the reloader to flush its cache
        self._cached_reloader.new_generation()

        # Reload the looper class
        m = self._cached_reloader.get_module(inspect.getmodule(self.looper))
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
                    if inspect.getsource(value)\
                       != inspect.getsource(vars(old_lc_instance)[name]):
                        self.looper.__dict__[name] = value
                except KeyError:
                    # New function
                    logging.debug("KeyError")
                    self.looper.__dict__[name] = value
            elif isinstance(value, types.InstanceType):
                # TODO: implement this
                pass
            else:
                try:
                    if value != vars(old_lc_instance)[name]:
                        logging.debug("%s %s, %s", name, value, vars(old_lc_instance)[name])
                        self.looper.__dict__[name] = value
                except KeyError:
                    # The property is a new one
                    logging.debug("property KeyError")
                    self.looper.__dict__[name] = value
        self.looper.__class__ = lc

        # Reload the rest
        for k, v in self.looper.loop_body.func_globals.items():
            if k != "__builtins__":
                if isinstance(v, types.ModuleType):
                    if not v.__name__.startswith("pygame"):
                        self.looper.loop_body.func_globals[k] =\
                            self._cached_reloader.get_module(v)
                elif isinstance(v, types.FunctionType):
                    m = self._cached_reloader.get_module(inspect.getmodule(v))
                    new_v = m.__getattribute__(v.__name__)
                    self.looper.loop_body.func_globals[k] = new_v
                elif isinstance(v, types.InstanceType):
                    logging.debug("object")

    def _loop(self):
        while self.running:
            try:
                if self.updated:
                    self.updated = False
                    self._do_update()
                if self.looper.loop_body():
                    self.running = False
            except Exception:
                traceback.print_exc()
                if self.debug_on_exception:
                    ipdb.set_trace()
                else:
                    time.sleep(5)
