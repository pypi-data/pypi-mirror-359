from typing import Any, Iterable, Mapping


class DictProxy(Mapping, Iterable, list):
    def __init__(self, obj: Any):
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
        if key in self.__deleted:
            self.__deleted.remove(key)
        self.__values[key] = value

    def __getitem__(self, key: str):
        if key in self.__deleted:
            raise KeyError(key)
        if key in self.__values:
            return self.__values[key]
        if self.__is_mapping:
            return self.__obj[key]
        return getattr(self.__obj, key)

    def __delitem__(self, key: str):
        if key in self.__values:
            del self.__values[key]
        self.__deleted.append(key)

    def __setattr__(self, key: str, value: Any):
        if key.startswith(f'_{self.__class__.__name__}'):
            object.__setattr__(self, key, value)
        else:
            self.__setitem__(key, value)

    __getattr__ = __getitem__
    __delattr__ = __delitem__

    def __iter__(self):
        if self.__is_mapping:
            _obj_keys = self.__obj.keys()
        else:
            try:
                _obj_keys = (it for it in self.__obj.__dict__.keys() if not it.startswith('__'))
            except KeyError:
                _obj_keys = tuple()

        yield from sorted(it for it in {*_obj_keys, *self.__values.keys()} if it not in self.__deleted)

    def __contains__(self, key: str):
        if key in self.__deleted:
            return False
        if key in self.__values:
            return True
        if self.__is_mapping:
            return key in self.__obj
        return hasattr(self.__obj, key)

    def __len__(self):
        return list.__len__(self)

    def items(self):
        return [(key, self[key]) for key in self]

    def keys(self):
        return list(self)

    def values(self):
        return [self[key] for key in self]

    def get(self, key: str, default: Any = None):
        if key in self:
            return self[key]
        return default
