from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn, TypeVar

from typing_extensions import Self, override

from eascheduler.errors import InfiniteLoopDetectedError


if TYPE_CHECKING:
    from collections.abc import Generator

    from whenever import Instant, SystemDateTime


class CompareEqualityBySlotValues:
    __slots__ = ()

    # Since all classes use slots we can compare them by comparing their slot values
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError()
        return all(getattr(self, s) == getattr(other, s) for s in self.__slots__)


class ProducerFilterBase(CompareEqualityBySlotValues):
    __slots__ = ()

    def allow(self, dt: SystemDateTime) -> bool:
        raise NotImplementedError()

    def copy(self) -> Self:
        raise NotImplementedError()


DTPB_TYPE = TypeVar('DTPB_TYPE', bound='DateTimeProducerBase')


class DateTimeProducerBase(CompareEqualityBySlotValues):
    __slots__ = ('_filter', )

    def __init__(self) -> None:
        self._filter: ProducerFilterBase | None = None

    def get_next(self, dt: Instant) -> Instant:
        """Get the next date time after the given date time.
        Has to guarantee that the returned date time is after the given date time."""
        raise NotImplementedError()

    def _copy_filter(self, obj: DTPB_TYPE) -> DTPB_TYPE:
        obj._filter = self._filter.copy() if self._filter is not None else None
        return obj

    def copy(self) -> Self:
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
