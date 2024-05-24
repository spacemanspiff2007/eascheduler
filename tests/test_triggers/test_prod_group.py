from pendulum import DateTime, Timezone

from eascheduler.producers.prod_filter import DayOfWeekProducerFilter
from eascheduler.producers.prod_group import GroupProducer
from eascheduler.producers.prod_interval import IntervalProducer


def dt(day, hour):
    return DateTime(2001, 1, day, hour, tzinfo=Timezone('Europe/Berlin'))


def test_simple():

    p1 = IntervalProducer(dt(1, 8), 3600 * 5)   # 8, 13, 18, 23
    p2 = IntervalProducer(dt(1, 8), 3600 * 3)   # 8, 11, 14, 17

    p = GroupProducer([p1, p2])

    assert p.get_next(dt(1, 6)) == dt(1, 8)
    assert p.get_next(dt(1, 8)) == dt(1, 11)
    assert p.get_next(dt(1, 11)) == dt(1, 13)
    assert p.get_next(dt(1, 13)) == dt(1, 14)
    assert p.get_next(dt(1, 14)) == dt(1, 17)
    assert p.get_next(dt(1, 17)) == dt(1, 18)


def test_filter():
    p1 = IntervalProducer(dt(1, 8), 3600 * 5)   # 8, 13, 18, 23, 4, 9
    p2 = IntervalProducer(dt(1, 8), 3600 * 3)   # 8, 11, 14, 17, 20, 23, 2, 5

    p = GroupProducer([p1, p2])
    p._filter = DayOfWeekProducerFilter([2])

    assert p.get_next(dt(1, 6)) == dt(2, 2)
    assert p.get_next(dt(2, 2)) == dt(2, 4)
    assert p.get_next(dt(2, 4)) == dt(2, 5)
