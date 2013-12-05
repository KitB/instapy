""" Replacing the builtin object class with a class that will track all objects
    created.

    The important advantage of this over using gc.get_objects() is that we can
    determine a portion of code in which to modify classes such that they are
    tracked. For instapy this means we won't be influencing builtins or portions
    of instapy.

    On the other hand such behaviour could be achieved by other means. Possibly
    using decorators allowing the programmer to tag things as updatable. Such a
    mechanism would avoid the fairly significant drawbacks of using weakrefs to
    avoid a memory leak here."""
import __builtin__
import weakref

# NOTE: There are a whole bunch of things that cannot be stored in this.
tracked_objects = weakref.WeakSet()

original_object = object


class TrackingObject(object):
    def __new__(cls, *args, **kwargs):
        i = super(TrackingObject, cls).__new__(cls, *args, **kwargs)
        tracked_objects.add(i)
        return i


class ReplacedContext(object):
    def __enter__(self):
        self.old_object = object
        __builtin__.object = TrackingObject

    def __exit__(self, exc_type, exc_value, traceback):
        __builtin__.object = self.old_object


def install():
    __builtin__.object = TrackingObject


def uninstall():
    __builtin__.object = original_object
