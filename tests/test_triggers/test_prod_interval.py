from pendulum import DateTime, Timezone

from eascheduler.producers.prod_filter import DayOfWeekProducerFilter
from eascheduler.producers.prod_interval import IntervalProducer


def dt(day, hour):
    return DateTime(2001, 1, day, hour, tzinfo=Timezone('Europe/Berlin'))


def test_simple():
    tz = Timezone('Europe/Berlin')
    dt_start = DateTime(2001, 1, 1, tzinfo=tz)
    dt_now = dt_start

    p = IntervalProducer(DateTime(2001, 1, 1, 8, tzinfo=tz), 3600 * 5)

    for v in range(3, 100, 5):
        days = v // 24
        hours = v % 24
        for _ in range(20):
            assert p.get_next(dt_now) == dt(dt_start.day + days, hours)
        dt_now = dt(dt_start.day + days, hours)


def test_filter():
    producer = IntervalProducer(dt(1, 8), 3600 * 12)

    assert producer.get_next(dt(1, 7)) == dt(1, 8)
    assert producer.get_next(dt(1, 8)) == dt(1, 20)
    assert producer.get_next(dt(1, 20)) == dt(2, 8)

    producer._filter = DayOfWeekProducerFilter([6])
    assert producer.get_next(dt(1, 7)) == dt(6, 8)
    assert producer.get_next(dt(6, 8)) == dt(6, 20)
    assert producer.get_next(dt(6, 20)) == dt(13, 8)
