from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn

from typing_extensions import override

from eascheduler.errors import InfiniteLoopDetectedError


if TYPE_CHECKING:
    from collections.abc import Generator

    from whenever import Instant, SystemDateTime


class ProducerFilterBase:
    __slots__ = ()

    def allow(self, dt: SystemDateTime) -> bool:
        raise NotImplementedError()


class DateTimeProducerBase:
    __slots__ = ('_filter', )

    def __init__(self) -> None:
        self._filter: ProducerFilterBase | None = None

    def get_next(self, dt: Instant) -> Instant:
        """Get the next date time after the given date time.
        Has to guarantee that the returned date time is after the given date time."""
        raise NotImplementedError()


class DateTimeProducerOperationBase(DateTimeProducerBase):
    __slots__ = ('_producer', )

    def __init__(self, producer: DateTimeProducerBase) -> None:
        super().__init__()
        self._producer: DateTimeProducerBase = producer

    def apply_operation(self, next_dt: Instant, dt: Instant) -> Instant:
        raise NotImplementedError()

    @override
    def get_next(self, dt: Instant) -> Instant:   # type: ignore[return]
        next_dt = dt

        for _ in not_infinite_loop():  # noqa: RET503
            next_dt = self._producer.get_next(next_dt)
            value = self.apply_operation(next_dt, dt)

            if value > dt and ((f := self._filter) is None or f.allow(value.to_system_tz())):
                return value


def not_infinite_loop() -> Generator[int, None, NoReturn]:
    yield from range(1, 100_000)

    raise InfiniteLoopDetectedError()
