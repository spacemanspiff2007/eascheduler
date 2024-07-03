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


class ProducerObject:
    def __init__(self, producer: DateTimeProducerBase):
        self._producer: Final[DateTimeProducerBase] = producer

    def offset(self, offset: int) -> ProducerObject:
        return ProducerObject(OffsetProducerOperation(self._producer, offset))

    def earliest(self, earliest: dt_time) -> ProducerObject:
        return ProducerObject(EarliestProducerOperation(self._producer, earliest))

    def latest(self, latest: dt_time) -> ProducerObject:
        return ProducerObject(LatestProducerOperation(self._producer, latest))

    def jitter(self, low: int, high: int | None = None) -> ProducerObject:
        return ProducerObject(JitterProducerOperation(self._producer, low, high))

    def only_on(self, filter: FilterObject):  # noqa: A002
        if self._producer._filter is not None:
            raise ValueError()
        self._producer._filter = filter._filter
        return self

    only_at = only_on


class ProducerBuilder:
    @staticmethod
    def dawn() -> ProducerObject:
        return ProducerObject(DawnProducer())

    @staticmethod
    def sunrise() -> ProducerObject:
        return ProducerObject(SunriseProducer())

    @staticmethod
    def noon() -> ProducerObject:
        return ProducerObject(NoonProducer())

    @staticmethod
    def sunset() -> ProducerObject:
        return ProducerObject(SunsetProducer())

    @staticmethod
    def dusk() -> ProducerObject:
        return ProducerObject(DuskProducer())

    @staticmethod
    def group(*builders: ProducerObject) -> ProducerObject:
        return ProducerObject(GroupProducer([b._producer for b in builders]))

    @staticmethod
    def interval(start: T_HINT, interval: dt_timedelta | int) -> ProducerObject:
        return ProducerObject(IntervalProducer(get_utc(start), interval))

    @staticmethod
    def time(time: dt_time) -> ProducerObject:
        return ProducerObject(TimeProducer(time))
