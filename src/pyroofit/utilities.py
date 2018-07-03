# -*- coding: utf-8 -*-
"""
Some utility constructs.

"""

import logging
import collections
import inspect
import functools


class Mixin(object):
    def __init__(self, *args, **kwds):
        """Sentinel for collaborative super class to init"""
        pass


class ClassLoggingMixin(object):
    """Mixin class that enables logging for instances of a specific class

    """
    def __init__(self, *args, **kwds):
        """Initialise the logger instance"""
        super(ClassLoggingMixin, self).__init__(*args, **kwds)
        self.logger = logging.getLogger(self.__class__.__name__)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(self, msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def unknown_error(self):
        self.logger.error("Unknown Error occured o_O")

    @staticmethod
    def setup_basic_config():
        logging.basicConfig(level=logging.DEBUG,
                            format='%(name)-18s \t %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M')


class AttrDict(dict):
    """Dictionary which items can also be addressed by attribute lookup in addition to item lookup"""
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def check_kwds(keys):
    """Decorator factory for decorators checking for valid keyword argument names

    """
    def decorator(func):
        """Decorator applying a check for valid keyword argument names to the function"""
        valid_keys = set(keys)
        valid_keys.update(inspect.signature(func).args)
        @functools.wraps(func)
        def decorated(*args, **kwds):
            for key in kwds:
                if key not in valid_keys:
                    raise ArgumentError("Unallowed keyword argument " + key)
            return func(*args, **kwds)

        return decorated
    return decorator


def is_iterable(obj):
    """Check if an object is iterable

    Args:
        obj (object): Generic object

    Returns:
        True if is able to use python iterations

    """
    return isinstance(obj, collections.Iterable)


class Singleton(object):
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, cls):
        self._decorated = cls

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)
