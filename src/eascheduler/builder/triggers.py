from __future__ import annotations

from typing import TYPE_CHECKING, Final

from eascheduler.builder.helper import T_HINT, get_utc
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

    from eascheduler.builder.filters import FilterObject
    from eascheduler.producers.base import DateTimeProducerBase


# noinspection PyShadowingBuiltins,PyProtectedMember
class TriggerObject:
    def __init__(self, producer: DateTimeProducerBase):
        self._producer: Final[DateTimeProducerBase] = producer

    def offset(self, offset: int) -> TriggerObject:
        return TriggerObject(OffsetProducerOperation(self._producer, offset))

    def earliest(self, earliest: dt_time) -> TriggerObject:
        return TriggerObject(EarliestProducerOperation(self._producer, earliest))

    def latest(self, latest: dt_time) -> TriggerObject:
        return TriggerObject(LatestProducerOperation(self._producer, latest))

    def jitter(self, low: int, high: int | None = None) -> TriggerObject:
        return TriggerObject(JitterProducerOperation(self._producer, low, high))

    def only_on(self, filter: FilterObject):  # noqa: A002
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
    def interval(start: T_HINT, interval: dt_timedelta | int) -> TriggerObject:
        return TriggerObject(IntervalProducer(get_utc(start), interval))

    @staticmethod
    def time(time: dt_time) -> TriggerObject:
        return TriggerObject(TimeProducer(time))
