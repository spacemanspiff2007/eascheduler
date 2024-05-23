from __future__ import annotations

from typing import TYPE_CHECKING, Generator, Literal

from eascheduler.errors import InfiniteLoopDetectedError


if TYPE_CHECKING:
    from pendulum import DateTime


class ProducerFilterBase:
    __slots__ = ()

    def skip(self, dt: DateTime) -> bool:
        raise NotImplementedError()


class DateTimeProducerBase:
    __slots__ = ('_filter', )

    def __init__(self):
        self._filter: ProducerFilterBase | None = None

    def get_next(self, dt: DateTime) -> DateTime:
        raise NotImplementedError()


class DateTimeOperationBase:
    __slots__ = ()

    def apply(self, dt: DateTime) -> DateTime | None:
        raise NotImplementedError()

    def __eq__(self, other):
        raise NotImplementedError()


def not_infinite_loop() -> Generator[Literal[True], None, None]:
    yield from range(1, 100_000)

    raise InfiniteLoopDetectedError()
