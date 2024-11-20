from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal

from typing_extensions import Self

from eascheduler.builder.helper import (
    HINT_CLOCK_BACKWARD,
    HINT_CLOCK_FORWARD,
    HINT_INSTANT,
    HINT_POS_TIMEDELTA,
    HINT_TIME,
    HINT_TIMEDELTA,
    BuilderTypeValidator,
    get_instant,
    get_pos_timedelta_secs,
    get_time_replacer,
    get_timedelta,
)
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
    SunAzimuthProducer,
    SunElevationProducer,
    SunriseProducer,
    SunsetProducer,
    TimeProducer,
)
from eascheduler.producers.base import DateTimeProducerBase


if TYPE_CHECKING:
    from eascheduler.builder.filters import FilterObject


# noinspection PyShadowingBuiltins,PyProtectedMember
class TriggerObject:
    def __init__(self, producer: DateTimeProducerBase) -> None:
        self._producer: Final[DateTimeProducerBase] = producer

    def offset(self, offset: HINT_TIMEDELTA) -> Self:
        """Offset the time returned by the trigger

        :param offset: The offset (positive or negative)
        """
        return self.__class__(
            OffsetProducerOperation(self._producer, get_timedelta(offset).in_seconds())
        )

    def earliest(self, earliest: HINT_TIME, *,
                 clock_forward: HINT_CLOCK_FORWARD = None, clock_backward: HINT_CLOCK_BACKWARD = None) -> Self:
        """Set the earliest time of day the trigger can fire.
        If the trigger would fire before the earliest time, the earliest time will be used instead.

        :param earliest: The time of day before the trigger can not fire
        :param clock_forward: How to handle the transition when the clock moves forward
        :param clock_backward: How to handle the transition when the clock moves backward
        """
        return self.__class__(
            EarliestProducerOperation(
                self._producer,
                get_time_replacer(earliest, clock_forward=clock_forward, clock_backward=clock_backward)
            )
        )

    def latest(self, latest: HINT_TIME, *,
               clock_forward: HINT_CLOCK_FORWARD = None, clock_backward: HINT_CLOCK_BACKWARD = None) -> Self:
        """Set the latest time of day the trigger can fire.
        If the trigger would fire after the latest time, the latest time will be used instead.

        :param latest: The time of day before the trigger can not fire
        :param clock_forward: How to handle the transition when the clock moves forward
        :param clock_backward: How to handle the transition when the clock moves backward
        """
        return self.__class__(
            LatestProducerOperation(
                self._producer,
                get_time_replacer(latest, clock_forward=clock_forward, clock_backward=clock_backward)
            )
        )

    def jitter(self, low: HINT_POS_TIMEDELTA, high: HINT_POS_TIMEDELTA | None = None) -> Self:
        """Add jitter to the time returned by the trigger.

        :param low: The lower bound of the jitter
        :param high: The upper bound of the jitter. If not specified the jitter will be 0 .. low
        """
        return self.__class__(
            JitterProducerOperation(
                self._producer,
                get_timedelta(low).in_seconds(), get_timedelta(high).in_seconds() if high is not None else None
            )
        )

    def only_on(self, filter: FilterObject) -> Self:  # noqa: A002
        """Add a filter to the trigger which can be used to allow or disallow certain times.

        :param filter: The filter to apply to the trigger
        """
        if self._producer._filter is not None:
            raise ValueError()
        self._producer._filter = filter._filter
        return self

    only_at = only_on


# noinspection PyProtectedMember
class TriggerBuilder:
    @staticmethod
    def dawn() -> TriggerObject:
        """Triggers at dawn."""
        return TriggerObject(DawnProducer())

    @staticmethod
    def sunrise() -> TriggerObject:
        """Triggers at sunrise."""
        return TriggerObject(SunriseProducer())

    @staticmethod
    def noon() -> TriggerObject:
        """Triggers at noon."""
        return TriggerObject(NoonProducer())

    @staticmethod
    def sunset() -> TriggerObject:
        """Triggers at sunset."""
        return TriggerObject(SunsetProducer())

    @staticmethod
    def dusk() -> TriggerObject:
        """Triggers at dusk."""
        return TriggerObject(DuskProducer())

    @staticmethod
    def sun_elevation(elevation: float, direction: Literal['rising', 'setting']) -> TriggerObject:
        """Triggers at a specific sun elevation

        :param elevation: Sun elevation in degrees
        :param direction: rising or falling
        """
        return TriggerObject(SunElevationProducer(elevation, direction))

    @staticmethod
    def sun_azimuth(azimuth: float) -> TriggerObject:
        """Triggers at a specific sun azimuth

        :param azimuth: Sun azimuth in degrees
        """
        return TriggerObject(SunAzimuthProducer(azimuth))

    @staticmethod
    def group(*builders: TriggerObject) -> TriggerObject:
        """Group multiple triggers together. The triggers will be checked and the trigger that runs next will be used

        :param builders: Triggers that should be grouped together
        """

        return TriggerObject(GroupProducer([_get_producer(b) for b in builders]))

    @staticmethod
    def interval(start: HINT_INSTANT, interval: HINT_POS_TIMEDELTA) -> TriggerObject:
        """Triggers at a fixed interval from a given start time.

        :param start: When this trigger will run for the first time.
                      Note: It's not possible to specify a start time
                      greater than the interval time. Since the producer is stateless it will automatically select
                      the next appropriate run time.
                      Example: start 90 minutes, interval 60 minutes -> first run will be in 30 minutes.
                      This makes it easy to ensure that the job will always run at a certain time by
                      specifying the start time isntead of a delta and the interval.
                      E.g. start ``00:15:00`` and interval 1 hour
        :param interval: The interval how this trigger will be repeated
        """
        return TriggerObject(
            IntervalProducer(get_instant(start) if start is not None else None, get_pos_timedelta_secs(interval))
        )

    @staticmethod
    def time(time: HINT_TIME, *,
             clock_forward: HINT_CLOCK_FORWARD = None, clock_backward: HINT_CLOCK_BACKWARD = None) -> TriggerObject:
        """Triggers at a specific time of day. When the time of day is during a daylight saving time transition
        it has to be explicitly specified how the transition should be handled.

        :param time: The time of day the trigger should fire
        :param clock_forward: How to handle the transition when the clock moves forward
        :param clock_backward: How to handle the transition when the clock moves backward
        """
        return TriggerObject(
            TimeProducer(
                get_time_replacer(time, clock_forward=clock_forward, clock_backward=clock_backward)
            )
        )


_get_producer = BuilderTypeValidator(TriggerObject, DateTimeProducerBase, '_producer')
