import imp
import inspect
import ipdb
import logging
import sys
import threading
import time
import traceback
import types

import pygame


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


def is_user_class(obj):
    cls = obj.__class__
    if hasattr(cls, '__class__'):
        return ('__dict__' in dir(cls) or hasattr(cls, '__slots__'))
    return False


class CachedReloader(object):
    """Provides a cached import mechanism.

       Allows the programmer to reset this cache between "generations"
    """
    def __init__(self):
        # TODO: Just use the built in reload mechanism and keep generations by
        # copying sys.modules. Didn't work.
        self._generations = []  # TODO: Use a deque
        self._generations.append(dict())

    def new_generation(self):
        """Reset the cache."""
        self._generations.append(dict())

    @property
    def _modules(self):
        return self._generations[-1]

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


class Looper(type):
    """ Metaclass that will manage running the __init_once__ method properly"""
    def __call__(cls, *args, **kwargs):
        self = cls.__new__(cls, *args, **kwargs)
        if kwargs.get('__instapy_first_run__', True):
            self.__init_once__()
        try:
            del kwargs['__instapy_first_run__']
        except KeyError:
            pass
        self.__init__(*args, **kwargs)
        return self


class ObjectSet(object):
    # TODO: Implement a set that uses "is" for equality
    def __init__(self):
        self._d = {}

    def add(self, current, old_initial, new_initial):
        self._d[id(current)] = (current, old_initial, new_initial)

    def pop(self):
        return self._d.popitem()[1]

    def __nonzero__(self):
        return bool(self._d)


def get_vars_iter(obj):
    try:
        for name, value in vars(obj).iteritems():
            yield (name, value)
    except TypeError:
        for name in dir(obj):
            yield (name, getattr(obj, name))


class Reloader(threading.Thread):
    def __init__(self, looper, debug_on_exception=True, *args, **kwargs):
        super(Reloader, self).__init__(*args, **kwargs)
        self.daemon = True
        self.updated = False
        self.restarted = False
        self.running = False
        self.name = "Game Thread"
        self.looper = looper
        self.debug_on_exception = debug_on_exception
        self._cached_reloader = CachedReloader()

    def update(self):
        self.updated = True

    def restart(self):
        self.restarted = True

    def run(self):
        self.running = True
        self._loop()
        logging.info("Reloader finished")

    def _loop(self):
        while self.running:
            try:
                if self.updated:
                    self.updated = False
                    self._do_update()
                if self.restarted:
                    self.restarted = False
                    self.looper.__init__()
                if self.looper.loop_body():
                    self.running = False
            except Exception:
                traceback.print_exc()
                if self.debug_on_exception:
                    pygame.event.set_grab(False)
                    pygame.mouse.set_visible(True)
                    ipdb.post_mortem(sys.exc_info()[2])
                else:
                    time.sleep(5)

    def _update_object(self, current, old_initial, new_initial):
        logging.debug("Updating (%s)" % current)

        m = self._cached_reloader.get_module(inspect.getmodule(current))
        cls = m.__getattribute__(current.__class__.__name__)

        current.__class__ = cls

        def _upd(name, value):
            logging.debug("Updating: name (%s), value (%s)", name, value)
            if name == "__class__":
                return
            elif inspect.isbuiltin(value):
                return
            elif inspect.ismethod(value) \
                    or value.__class__.__name__ == 'method-wrapper':
                return
            elif inspect.isroutine(value):
                try:
                    if inspect.getsource(value)\
                       != inspect.getsource(getattr(old_initial, name)):
                        setattr(current, name, value)
                except KeyError:
                    # New function
                    logging.debug("New function added:\n\t"
                                  "%s:     %s",
                                  name, value)
                    setattr(current, name, value)
            elif is_user_class(value):
                new_initial_sub = value
                try:
                    current_sub = getattr(current, name)
                    old_initial_sub = getattr(old_initial, name)
                except AttributeError:
                    logging.debug("New initial added:\n\t"
                                  "New:     %s",
                                  new_initial_sub)
                    setattr(current, name, value)
                    return
                logging.debug("Adding to frontier:\n\t"
                              "Old:     %s\n\t"
                              "Current: %s\n\t"
                              "New:     %s",
                              old_initial_sub, current_sub, new_initial_sub)
                self.objects_to_update.add(
                    current_sub, old_initial_sub, new_initial_sub)
            else:
                try:
                    if value != getattr(old_initial, name):
                        logging.debug("Value of %s changed:\n\t"
                                      "Old: %s\n\t"
                                      "New: %s",
                                      name, getattr(old_initial, name), value)
                        setattr(current, name, value)
                except KeyError:
                    # The property is a new one
                    logging.debug("New property:\n\t"
                                  "New:     %s",
                                  value)
                    setattr(current, name, value)
                except AttributeError:
                    # Just trying this to squash funny bits with pygame.Color
                    logging.debug("property AttributeError")
                    pass

        for name, value in get_vars_iter(new_initial):
            _upd(name, value)

    def _do_update(self):
        # TODO: Unify the update methods for looper instance and other objects
        # TODO: Replace the init method with an __init__ method; replace
        #       init_once with __init_once__
        logging.debug("Updating")
        # Tell the reloader to flush its cache
        self._cached_reloader.new_generation()

        self.objects_to_update = ObjectSet()

        # Reload the looper class
        m = self._cached_reloader.get_module(inspect.getmodule(self.looper))
        lc = m.__getattribute__(self.looper.__class__.__name__)
        lc_instance = lc(__instapy_first_run__=False)
        old_lc_instance = self.looper.__class__(__instapy_first_run__=False)

        self.objects_to_update.add(self.looper, old_lc_instance, lc_instance)
        while self.objects_to_update:
            stuff = self.objects_to_update.pop()
            self._update_object(*stuff)

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
                elif is_user_class(v):
                    # TODO: Should it ever get here?
                    #       If so what do we do?
                    # NOTE: It gets here. What do we do?
                    # NOTE: Of course it gets here.
                    # logging.debug(value)
                    pass
