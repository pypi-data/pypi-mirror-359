from functools import wraps
from typing import Callable

from frozendict import frozendict


class classproperty:
    """
    A decorator that allows creating properties at the class level.

    This decorator enables the creation of properties that can be accessed
    directly from the class, without needing to instantiate it.

    Example:
        >>> class MyClass:
        ...     _value = 10
        ...
        ...     @classproperty
        ...     def value(cls):
        ...         return cls._value
        ...
        >>> # Access the property at the class level
        >>> print(MyClass.value)  # Output: 10
        10
    """
    def __init__(self, method: Callable):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self


class cachedproperty:
    """
    A decorator that caches the result of a property method.

    This decorator is similar to the built-in @property decorator, but it caches
    the result of the method call in the instance's __dict__, so subsequent
    accesses don't recompute the value.

    Example:
        >>> class MyClass:
        ...     @cachedproperty
        ...     def expensive_calculation(self):
        ...         # This will only be calculated once per instance
        ...         return sum(range(10000000))
        ...
        >>> obj = MyClass()
        >>> print(obj.expensive_calculation)  # Calculated
        49999995000000
        >>> print(obj.expensive_calculation)  # Retrieved from cache
        49999995000000
    """
    name = None

    @staticmethod
    def func(instance):
        raise TypeError('Cannot use cachedproperty instance without calling __set_name__() on it.')

    def __init__(self, method: Callable):
        self.real_func = method
        self.__doc__ = getattr(method, '__doc__')

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name
            self.func = self.real_func
        elif name != self.name:
            raise TypeError(f'Cannot assign the same cachedproperty to two different names ({self.name} and {name}).')

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


class cachedclassproperty:
    """
    A decorator that combines the functionality of classproperty and cachedproperty.

    This decorator enables the creation of properties that can be accessed
    directly from the class, without needing to instantiate it, and caches
    the result to avoid recomputation on subsequent accesses.

    Example:
        >>> class MyClass:
        ...     @cachedclassproperty
        ...     def expensive_class_calculation(cls):
        ...         # This will only be calculated once for the class
        ...         return sum(range(10000000))
        ...
        >>> print(MyClass.expensive_class_calculation)  # Calculated
        49999995000000
        >>> print(MyClass.expensive_class_calculation)  # Retrieved from cache
        49999995000000
    """
    name = None

    @staticmethod
    def func(instance):
        raise TypeError('Cannot use cachedproperty instance without calling __set_name__() on it.')

    def __init__(self, method: Callable):
        self.real_func = method
        self.fget = method
        self.__doc__ = getattr(method, '__doc__')

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name
            self.func = self.real_func
        elif name != self.name:
            raise TypeError(f'Cannot assign the same cachedproperty to two different names ({self.name} and {name}).')

    def __get__(self, instance, cls=None):
        setattr(cls, self.name, self.func(cls))
        return getattr(cls, self.name)

    def getter(self, method):
        self.fget = method
        return self


def freezeargs(fn):
    """
    A decorator that freezes dictionary arguments to make them immutable.

    This decorator converts any dictionary arguments to frozendict instances,
    which prevents accidental modification of the dictionaries.

    Parameters:
        fn (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.

    Example:
        >>> @freezeargs
        ... def process_config(config):
        ...     # config is now immutable
        ...     # This prevents accidental modification of the config
        ...     return config['value']
        ...
        >>> process_config({'value': 42})
        42
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        args = ((frozendict(v) if isinstance(v, dict) else v) for v in args)
        kwargs = {k: (frozendict(v) if isinstance(v, dict) else v) for k, v in kwargs.items()}
        return fn(*args, **kwargs)

    return wrapper
