import os
from typing import Any, Optional, Type, Union


def to_bool(value: Union[str, int, bool]) -> bool:
    if isinstance(value, str):
        return value.lower() in ('true', 't', '1')
    return bool(value)


def to_int(value: Union[str, int], default: int = None) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_list(value: str, cast: Type = None, separator: str = ',') -> list[Any]:
    result = []
    if isinstance(value, str):
        result = [v for v in value.split(separator) if v]
    return [cast(v) for v in result] if callable(cast) else result


def get_bool(name: str, default: bool = False) -> bool:
    return to_bool(os.environ.get(name)) or default


def get_int(name: str, default: int = None) -> int | None:
    return val if (val := to_int(os.environ.get(name))) is not None else default


def get_list(name: str, cast: Type = None, separator: str = ',', default: list[Any] = None) -> list[Any]:
    return val if (val := to_list(os.environ.get(name), cast, separator)) is not None else (default or [])
