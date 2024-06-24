from eascheduler.producers.prod_filter import DayOfWeekProducerFilter
from eascheduler.producers.prod_group import GroupProducer
from eascheduler.producers.prod_interval import IntervalProducer
from tests.helper import get_german_as_utc


def test_simple():

    p1 = IntervalProducer(get_german_as_utc(1, 1, 8), 3600 * 5)   # 8, 13, 18, 23
    p2 = IntervalProducer(get_german_as_utc(1, 1, 8), 3600 * 3)   # 8, 11, 14, 17

    p = GroupProducer([p1, p2])

    # ensure that it's stateless
    for _ in range(10):
        assert p.get_next(get_german_as_utc(1, 1, 6)) == get_german_as_utc(1, 1, 8)
        assert p.get_next(get_german_as_utc(1, 1, 8)) == get_german_as_utc(1, 1, 11)
        assert p.get_next(get_german_as_utc(1, 1, 11)) == get_german_as_utc(1, 1, 13)
        assert p.get_next(get_german_as_utc(1, 1, 13)) == get_german_as_utc(1, 1, 14)
        assert p.get_next(get_german_as_utc(1, 1, 14)) == get_german_as_utc(1, 1, 17)
        assert p.get_next(get_german_as_utc(1, 1, 17)) == get_german_as_utc(1, 1, 18)


def test_filter():
    p1 = IntervalProducer(get_german_as_utc(1, 1, 8), 3600 * 5)   # 8, 13, 18, 23, 4, 9
    p2 = IntervalProducer(get_german_as_utc(1, 1, 8), 3600 * 3)   # 8, 11, 14, 17, 20, 23, 2, 5

    p = GroupProducer([p1, p2])
    p._filter = DayOfWeekProducerFilter([2])

    # ensure that it's stateless
    for _ in range(10):
        assert p.get_next(get_german_as_utc(1, 1, 6)) == get_german_as_utc(1, 2, 2)
        assert p.get_next(get_german_as_utc(1, 2, 2)) == get_german_as_utc(1, 2, 4)
        assert p.get_next(get_german_as_utc(1, 2, 4)) == get_german_as_utc(1, 2, 5)
        assert p.get_next(get_german_as_utc(1, 2, 23)) == get_german_as_utc(1, 9, 1)