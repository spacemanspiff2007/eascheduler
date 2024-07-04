from __future__ import annotations

from typing import TYPE_CHECKING, Literal, NoReturn

from typing_extensions import override

from eascheduler.errors import InfiniteLoopDetectedError


if TYPE_CHECKING:
    from collections.abc import Generator

    from whenever import LocalSystemDateTime, UTCDateTime


class ProducerFilterBase:
    __slots__ = ()

    def allow(self, dt: LocalSystemDateTime) -> bool:
        raise NotImplementedError()


class DateTimeProducerBase:
    __slots__ = ('_filter', )

    def __init__(self) -> None:
        self._filter: ProducerFilterBase | None = None

    def get_next(self, dt: UTCDateTime) -> UTCDateTime:
        """Get the next date time after the given date time.
        Has to guarantee that the returned date time is after the given date time."""
        raise NotImplementedError()


class DateTimeProducerOperationBase(DateTimeProducerBase):
    __slots__ = ('_producer', )

    def __init__(self, producer: DateTimeProducerBase) -> None:
        super().__init__()
        self._producer: DateTimeProducerBase = producer

    def apply_operation(self, next_dt: UTCDateTime, dt: UTCDateTime) -> UTCDateTime:
        raise NotImplementedError()

    @override
    def get_next(self, dt: UTCDateTime) -> UTCDateTime:   # type: ignore[return]
        next_dt = dt

        for _ in not_infinite_loop():  # noqa: RET503
            next_dt = self._producer.get_next(next_dt)
            value = self.apply_operation(next_dt, dt)

            if value > dt and ((f := self._filter) is None or f.allow(value.as_local())):
                return value


def not_infinite_loop() -> Generator[int, None, NoReturn]:
    yield from range(1, 100_000)

    raise InfiniteLoopDetectedError()
