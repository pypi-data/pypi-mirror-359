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
    def __init__(self, **kwargs):
        kwargs.setdefault('ensure_ascii', False)
        super().__init__(**kwargs)

    def default(self, o):
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
    return json.load(fp, cls=cls, **kwargs)


def loads(data: Union[str, bytes], *, cls: Type[json.JSONDecoder] = None, **kwargs):
    return json.loads(data, cls=cls, **kwargs)


def dump(obj: Any, fp: IO, *, ensure_ascii: bool = False, cls: Type[json.JSONEncoder] = None, indent: int = None, **kwargs):
    return json.dump(obj, fp, ensure_ascii=ensure_ascii, cls=cls or JSONEncoder, indent=indent, **kwargs)


def dumps(obj: Any, *, ensure_ascii: bool = False, cls: Type[json.JSONEncoder] = None, indent: int = None, **kwargs):
    return json.dumps(obj, ensure_ascii=ensure_ascii, cls=cls or JSONEncoder, indent=indent, **kwargs)
