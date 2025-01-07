
from eascheduler.builder import TriggerBuilder
from eascheduler.producers import (
    EarliestProducerOperation,
    IntervalProducer,
    JitterProducerOperation,
    LatestProducerOperation,
    OffsetProducerOperation,
    SunAzimuthProducerCompare,
    SunElevationProducerCompare,
    TimeProducer,
)


def test_trigger_producer_names() -> None:
    for name in ('Dawn', 'Sunrise', 'Noon', 'Sunset', 'Dusk'):
        obj = getattr(TriggerBuilder, name.lower())()._producer
        assert obj.__class__.__name__ == f'{name}Producer'

    assert isinstance(TriggerBuilder.time('12:00:00')._producer, TimeProducer)
    assert isinstance(TriggerBuilder.interval(1, 2)._producer, IntervalProducer)
    assert isinstance(TriggerBuilder.sun_elevation(5, 'rising')._producer, SunElevationProducerCompare)
    assert isinstance(TriggerBuilder.sun_azimuth(5)._producer, SunAzimuthProducerCompare)


def test_trigger_producer_operation_names() -> None:
    assert isinstance(TriggerBuilder.time('12:00:00').offset(1)._producer, OffsetProducerOperation)
    assert isinstance(TriggerBuilder.time('12:00:00').earliest('12:00:00')._producer, EarliestProducerOperation)
    assert isinstance(TriggerBuilder.time('12:00:00').latest('12:00:00')._producer, LatestProducerOperation)
    assert isinstance(TriggerBuilder.time('12:00:00').jitter(1, 2)._producer, JitterProducerOperation)


def test_producer_trigger_immutable() -> None:

    t = TriggerBuilder.interval(None, 2)

    o1 = t.offset(1)
    o1._producer._producer._interval = 3

    o2 = t.offset(2)
    o2._producer._producer._interval = 4

    t._producer._interval = 5
    assert o1._producer._producer._interval == 3
    assert o2._producer._producer._interval == 4
    assert t._producer._interval == 5
