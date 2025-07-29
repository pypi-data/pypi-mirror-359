from typing import Any, Iterable, Mapping, Dict, List, Tuple, Iterator


class DictProxy(Mapping, Iterable, list):
    """
    A proxy class that wraps a dictionary or object and allows modifications without changing the original.

    This class provides a dictionary-like interface to access and modify attributes of the wrapped object.
    Changes are stored in the proxy and don't affect the original object.

    The proxy can be used with both dictionary-like objects (implementing the Mapping interface)
    and regular objects (accessing attributes).

    Parameters:
        obj (Any): The object to wrap. Can be a dictionary or any other object.

    Example:
        >>> # With a dictionary
        >>> original = {'name': 'John', 'age': 30}
        >>> proxy = DictProxy(original)
        >>> proxy['age'] = 31  # Modify in proxy only
        >>> print(proxy['age'])  # Output: 31
        31
        >>> print(original['age'])  # Output: 30
        30

        >>> # With an object
        >>> class Person:
        ...     def __init__(self):
        ...         self.name = 'John'
        ...         self.age = 30

        >>> person = Person()
        >>> proxy = DictProxy(person)
        >>> proxy.age = 31  # Modify in proxy only
        >>> print(proxy.age)  # Output: 31
        31
        >>> print(person.age)  # Output: 30
        30
    """
    def __init__(self, obj: Any):
        """
        Initialize a new DictProxy instance.

        Parameters:
            obj (Any): The object to wrap. Can be a dictionary or any other object.
        """
        if isinstance(obj, DictProxy):
            self.__obj = obj.__obj
            self.__values = obj.__values
            self.__deleted = obj.__deleted
            self.__is_mapping = obj.__is_mapping
        else:
            self.__obj = obj
            self.__values = {}
            self.__deleted = []
            self.__is_mapping = isinstance(obj, Mapping)

    def __setitem__(self, key: str, value: any):
        """
        Set a value in the proxy.

        Parameters:
            key (str): The key to set.
            value (any): The value to set.
        """
        if key in self.__deleted:
            self.__deleted.remove(key)
        self.__values[key] = value

    def __getitem__(self, key: str):
        """
        Get a value from the proxy or the wrapped object.

        Parameters:
            key (str): The key to get.

        Returns:
            Any: The value for the key.

        Raises:
            KeyError: If the key is not found or has been deleted.
        """
        if key in self.__deleted:
            raise KeyError(key)
        if key in self.__values:
            return self.__values[key]
        if self.__is_mapping:
            return self.__obj[key]
        return getattr(self.__obj, key)

    def __delitem__(self, key: str):
        """
        Delete a key from the proxy.

        Parameters:
            key (str): The key to delete.
        """
        if key in self.__values:
            del self.__values[key]
        self.__deleted.append(key)

    def __setattr__(self, key: str, value: Any):
        """
        Set an attribute on the proxy.

        Parameters:
            key (str): The attribute name.
            value (Any): The value to set.
        """
        if key.startswith(f'_{self.__class__.__name__}'):
            object.__setattr__(self, key, value)
        else:
            self.__setitem__(key, value)

    # Allow attribute access to behave like dictionary access
    __getattr__ = __getitem__
    __delattr__ = __delitem__

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over all keys in the proxy and the wrapped object.

        Yields:
            str: Each key in the proxy and the wrapped object,
                 excluding deleted keys.
        """
        if self.__is_mapping:
            _obj_keys = self.__obj.keys()
        else:
            try:
                _obj_keys = (it for it in self.__obj.__dict__.keys() if not it.startswith('__'))
            except KeyError:
                _obj_keys = tuple()

        yield from sorted(it for it in {*_obj_keys, *self.__values.keys()} if it not in self.__deleted)

    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the proxy or the wrapped object.

        Parameters:
            key (str): The key to check.

        Returns:
            bool: True if the key exists and has not been deleted, False otherwise.
        """
        if key in self.__deleted:
            return False
        if key in self.__values:
            return True
        if self.__is_mapping:
            return key in self.__obj
        return hasattr(self.__obj, key)

    def __len__(self) -> int:
        """
        Get the number of keys in the proxy.

        Returns:
            int: The number of keys.
        """
        return list.__len__(self)

    def items(self) -> List[Tuple[str, Any]]:
        """
        Get all key-value pairs in the proxy.

        Returns:
            List[Tuple[str, Any]]: A list of (key, value) tuples.
        """
        return [(key, self[key]) for key in self]

    def keys(self) -> List[str]:
        """
        Get all keys in the proxy.

        Returns:
            List[str]: A list of keys.
        """
        return list(self)

    def values(self) -> List[Any]:
        """
        Get all values in the proxy.

        Returns:
            List[Any]: A list of values.
        """
        return [self[key] for key in self]

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the proxy with a default fallback.

        Parameters:
            key (str): The key to get.
            default (Any, optional): The default value to return if the key is not found.
                                    Default is None.

        Returns:
            Any: The value for the key, or the default if the key is not found.
        """
        if key in self:
            return self[key]
        return default
