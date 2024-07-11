from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import Self

from eascheduler.builder.helper import HINT_INSTANT, HINT_TIME, get_instant, get_time
from eascheduler.producers import (
    DawnProducer,
    DuskProducer,
    EarliestProducerOperation,
    GroupProducer,
    IntervalProducer,
    JitterProducerOperation,
    LatestProducerOperation,
    NoonProducer,
    OffsetProducerOperation,
    SunriseProducer,
    SunsetProducer,
    TimeProducer,
)


if TYPE_CHECKING:
    from datetime import time as dt_time
    from datetime import timedelta as dt_timedelta

    from whenever import Time

    from eascheduler.builder.filters import FilterObject
    from eascheduler.producers.base import DateTimeProducerBase


# noinspection PyShadowingBuiltins,PyProtectedMember
class TriggerObject:
    def __init__(self, producer: DateTimeProducerBase) -> None:
        self._producer: Final[DateTimeProducerBase] = producer

    def offset(self, offset: int) -> Self:
        return self.__class__(OffsetProducerOperation(self._producer, offset))

    def earliest(self, earliest: HINT_TIME) -> Self:
        return self.__class__(EarliestProducerOperation(self._producer, earliest))

    def latest(self, latest: HINT_TIME) -> Self:
        return self.__class__(LatestProducerOperation(self._producer, latest))

    def jitter(self, low: int, high: int | None = None) -> Self:
        return self.__class__(JitterProducerOperation(self._producer, low, high))

    def only_on(self, filter: FilterObject) -> Self:  # noqa: A002
        if self._producer._filter is not None:
            raise ValueError()
        self._producer._filter = filter._filter
        return self

    only_at = only_on


# noinspection PyProtectedMember
class TriggerBuilder:
    @staticmethod
    def dawn() -> TriggerObject:
        return TriggerObject(DawnProducer())

    @staticmethod
    def sunrise() -> TriggerObject:
        return TriggerObject(SunriseProducer())

    @staticmethod
    def noon() -> TriggerObject:
        return TriggerObject(NoonProducer())

    @staticmethod
    def sunset() -> TriggerObject:
        return TriggerObject(SunsetProducer())

    @staticmethod
    def dusk() -> TriggerObject:
        return TriggerObject(DuskProducer())

    @staticmethod
    def group(*builders: TriggerObject) -> TriggerObject:
        return TriggerObject(GroupProducer([b._producer for b in builders]))

    @staticmethod
    def interval(start: HINT_INSTANT, interval: dt_timedelta | int) -> TriggerObject:
        return TriggerObject(IntervalProducer(get_instant(start), interval))

    @staticmethod
    def time(time: HINT_TIME) -> TriggerObject:
        return TriggerObject(TimeProducer(get_time(time)))
