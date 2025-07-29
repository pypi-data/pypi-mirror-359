import datetime
import decimal
import json
import uuid
from json import JSONDecodeError, JSONDecoder
from typing import Any, IO, Type, Union

import frozendict

from dimtim.interfaces import Serializable
from dimtim.utils import duration, timezone

__all__ = [
    'dump', 'dumps', 'load', 'loads', 'JSONEncoder', 'JSONDecoder', 'JSONDecodeError'
]

compat_transforms = {}

try:
    from django.utils.functional import Promise

    compat_transforms[Promise] = lambda o: str(o)
except ImportError:
    pass

try:
    try:
        from pydantic.v1 import BaseModel

        compat_transforms[BaseModel] = lambda o: o.dict()

        from pydantic import BaseModel

        compat_transforms[BaseModel] = lambda o: o.model_dump()
    except ImportError:
        from pydantic import BaseModel

        compat_transforms[BaseModel] = lambda o: o.dict()
except ImportError:
    pass


class JSONEncoder(json.JSONEncoder):
    """
    Enhanced JSON encoder with support for additional Python types.

    This encoder extends the standard JSONEncoder to handle additional types:
    - sets and frozensets are converted to lists
    - datetime objects are converted to ISO format strings
    - timedelta objects are converted to ISO duration strings
    - Decimal and UUID objects are converted to strings
    - frozendict objects are converted to regular dicts
    - Serializable objects use their serialize() method
    - Django Promise objects (if available) are converted to strings
    - Pydantic models (if available) are converted using dict() or model_dump()

    Parameters:
        **kwargs: Additional arguments to pass to the parent JSONEncoder.
                 'ensure_ascii' is set to False by default.

    Example:
        >>> import json
        >>> from datetime import datetime
        >>> data = {
        ...     'timestamp': datetime.now(),
        ...     'tags': {'python', 'json', 'encoding'}
        ... }
        >>> json_str = json.dumps(data, cls=JSONEncoder)
        >>> print(json_str)  # Contains ISO format timestamp and tags as a list
    """
    def __init__(self, **kwargs):
        """
        Initialize the JSONEncoder with default settings.

        Parameters:
            **kwargs: Additional arguments to pass to the parent JSONEncoder.
                     'ensure_ascii' is set to False by default.
        """
        kwargs.setdefault('ensure_ascii', False)
        super().__init__(**kwargs)

    def default(self, o):
        """
        Convert Python objects to JSON-serializable types.

        This method is called for objects that are not natively serializable by json.

        Parameters:
            o: The object to serialize.

        Returns:
            A JSON-serializable version of the object.

        Raises:
            ValueError: If a timezone-aware time is encountered.
            TypeError: If an object cannot be serialized.
        """
        if isinstance(o, (set, frozenset)):
            return list(o)

        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()

        if isinstance(o, datetime.time):
            if timezone.is_aware(o):
                raise ValueError('JSON can\'t represent timezone-aware times.')
            return o.isoformat()

        if isinstance(o, datetime.timedelta):
            return duration.duration_iso_string(o)

        if isinstance(o, (decimal.Decimal, uuid.UUID)):
            return str(o)

        if isinstance(o, frozendict.frozendict):
            return dict(o)

        if isinstance(o, Serializable):
            return o.serialize()

        for t, fn in compat_transforms.items():
            if isinstance(o, t):
                return fn(o)

        return super().default(o)


def load(fp: IO, *, cls: Type[json.JSONDecoder] = None, **kwargs):
    """
    Deserialize a JSON file to a Python object.

    This is a wrapper around json.load that provides the same interface.

    Parameters:
        fp (IO): A file-like object with a read() method.
        cls (Type[json.JSONDecoder], optional): The decoder class to use. Default is None.
        **kwargs: Additional arguments to pass to json.load.

    Returns:
        Any: The deserialized Python object.

    Example:
        >>> with open('data.json', 'r') as f:
        ...     data = load(f)
    """
    return json.load(fp, cls=cls, **kwargs)


def loads(data: Union[str, bytes], *, cls: Type[json.JSONDecoder] = None, **kwargs):
    """
    Deserialize a JSON string to a Python object.

    This is a wrapper around json.loads that provides the same interface.

    Parameters:
        data (Union[str, bytes]): A JSON string.
        cls (Type[json.JSONDecoder], optional): The decoder class to use. Default is None.
        **kwargs: Additional arguments to pass to json.loads.

    Returns:
        Any: The deserialized Python object.

    Example:
        >>> json_str = '{"name": "John", "age": 30}'
        >>> data = loads(json_str)
        >>> print(data['name'])  # Output: "John"
        'John'
    """
    return json.loads(data, cls=cls, **kwargs)


def dump(obj: Any, fp: IO, *, ensure_ascii: bool = False, cls: Type[json.JSONEncoder] = None, indent: int = None, **kwargs):
    """
    Serialize a Python object to a JSON file.

    This is a wrapper around json.dump that uses the enhanced JSONEncoder by default
    and sets ensure_ascii to False by default.

    Parameters:
        obj (Any): The Python object to serialize.
        fp (IO): A file-like object with a write() method.
        ensure_ascii (bool, optional): If True, ensure the output contains only ASCII characters.
                                      Default is False.
        cls (Type[json.JSONEncoder], optional): The encoder class to use.
                                               Default is JSONEncoder.
        indent (int, optional): The number of spaces to indent for pretty-printing.
                               Default is None (no pretty-printing).
        **kwargs: Additional arguments to pass to json.dump.

    Returns:
        None

    Example:
        >>> from datetime import datetime
        >>> data = {
        ...     'timestamp': datetime.now(),
        ...     'message': 'Hello, world!'
        ... }
        >>> with open('output.json', 'w') as f:
        ...     dump(data, f, indent=2)  # Writes pretty-printed JSON with datetime in ISO format
    """
    return json.dump(obj, fp, ensure_ascii=ensure_ascii, cls=cls or JSONEncoder, indent=indent, **kwargs)


def dumps(obj: Any, *, ensure_ascii: bool = False, cls: Type[json.JSONEncoder] = None, indent: int = None, **kwargs):
    """
    Serialize a Python object to a JSON string.

    This is a wrapper around json.dumps that uses the enhanced JSONEncoder by default
    and sets ensure_ascii to False by default.

    Parameters:
        obj (Any): The Python object to serialize.
        ensure_ascii (bool, optional): If True, ensure the output contains only ASCII characters.
                                      Default is False.
        cls (Type[json.JSONEncoder], optional): The encoder class to use.
                                               Default is JSONEncoder.
        indent (int, optional): The number of spaces to indent for pretty-printing.
                               Default is None (no pretty-printing).
        **kwargs: Additional arguments to pass to json.dumps.

    Returns:
        str: The JSON string representation of the object.

    Example:
        >>> from datetime import datetime
        >>> data = {
        ...     'timestamp': datetime.now(),
        ...     'message': 'Hello, world!'
        ... }
        >>> json_str = dumps(data, indent=2)  # Pretty-printed JSON with datetime in ISO format
        >>> print(json_str)
    """
    return json.dumps(obj, ensure_ascii=ensure_ascii, cls=cls or JSONEncoder, indent=indent, **kwargs)
