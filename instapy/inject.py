""" A mechanism for causing objects to track their initialisation arguments.

    This is performed by adding a metaclass to the builtin object class."""
import __builtin__


original_object = object


class TrackingMeta(type):
    def __call__(cls, *args, **kwargs):
        i = type.__call__(cls, *args, **kwargs)
        i.__initial_arguments__ = (args, kwargs)
        return i


class TrackingObject(object):
    __metaclass__ = TrackingMeta


class ReplacedContext(object):
    def __init__(self, new_object=TrackingObject):
        self.new_object = new_object

    def __enter__(self):
        self.old_object = object
        __builtin__.object = self.new_object

    def __exit__(self, exc_type, exc_value, traceback):
        __builtin__.object = self.old_object


def install():
    __builtin__.object = TrackingObject


def uninstall():
    __builtin__.object = original_object
