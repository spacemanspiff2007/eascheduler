from __future__ import annotations

from typing import TYPE_CHECKING, Generator, Literal

from eascheduler.errors import InfiniteLoopDetectedError


if TYPE_CHECKING:
    from pendulum import DateTime


class ProducerBase:
    def get_next(self, dt: DateTime) -> DateTime:
        raise NotImplementedError()


class ProducerFilterBase:
    __slots__ = ()

    def allow(self, dt: DateTime) -> bool:
        raise NotImplementedError()


class DateTimeProducerBase(ProducerBase):
    __slots__ = ('_filter', )

    def __init__(self) -> None:
        self._filter: ProducerFilterBase | None = None


class DateTimeProducerOperationBase(ProducerBase):
    __slots__ = ('_producer', )

    def __init__(self, producer: DateTimeProducerBase) -> None:
        self._producer: DateTimeProducerBase = producer


def not_infinite_loop() -> Generator[Literal[True], None, None]:
    yield from range(1, 100_000)

    raise InfiniteLoopDetectedError()
