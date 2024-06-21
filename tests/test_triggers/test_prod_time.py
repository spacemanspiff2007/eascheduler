from datetime import time as dt_time

from pendulum import DateTime, Timezone

from eascheduler.producers import TimeProducer
from eascheduler.producers.prod_filter import DayOfWeekProducerFilter


def dt(day, hour):
    return DateTime(2001, 1, day, hour, tzinfo=Timezone('Europe/Berlin'))


def test_simple():
    producer = TimeProducer(dt_time(8))

    for _ in range(10):
        assert producer.get_next(dt(1, 7)) == dt(1, 8)
        assert producer.get_next(dt(1, 8)) == dt(2, 8)
        assert producer.get_next(dt(2, 8)) == dt(3, 8)


def test_filter():
    producer = TimeProducer(dt_time(8))
    producer._filter = DayOfWeekProducerFilter([6])

    for _ in range(10):
        assert producer.get_next(dt(1, 7)) == dt(6, 8)
        assert producer.get_next(dt(6, 8)) == dt(13, 8)
        assert producer.get_next(dt(13, 8)) == dt(20, 8)

