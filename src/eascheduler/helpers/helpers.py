from enum import Enum
from typing import TypeVar


T = TypeVar('T', bound=Enum)


def to_enum(enum: type[T], value: str) -> T:
    return enum(value) if not isinstance(value, enum) else value
