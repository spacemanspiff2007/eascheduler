from eascheduler.builder import TriggerBuilder
from eascheduler.producers import (
    EarliestProducerOperation,
    IntervalProducer,
    JitterProducerOperation,
    LatestProducerOperation,
    OffsetProducerOperation,
    SunAzimuthProducer,
    SunElevationProducer,
    TimeProducer,
)


def test_trigger_producer_names() -> None:
    for name in ('Dawn', 'Sunrise', 'Noon', 'Sunset', 'Dusk'):
        obj = getattr(TriggerBuilder, name.lower())()._producer
        assert obj.__class__.__name__ == f'{name}Producer'

    assert isinstance(TriggerBuilder.time('12:00:00')._producer, TimeProducer)
    assert isinstance(TriggerBuilder.interval(1, 2)._producer, IntervalProducer)
    assert isinstance(TriggerBuilder.sun_elevation(5, 'rising')._producer, SunElevationProducer)
    assert isinstance(TriggerBuilder.sun_azimuth(5)._producer, SunAzimuthProducer)


def test_trigger_producer_operation_names() -> None:
    assert isinstance(TriggerBuilder.time('12:00:00').offset(1)._producer, OffsetProducerOperation)
    assert isinstance(TriggerBuilder.time('12:00:00').earliest('12:00:00')._producer, EarliestProducerOperation)
    assert isinstance(TriggerBuilder.time('12:00:00').latest('12:00:00')._producer, LatestProducerOperation)
    assert isinstance(TriggerBuilder.time('12:00:00').jitter(1, 2)._producer, JitterProducerOperation)
