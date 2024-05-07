
from pendulum import DateTime

from eascheduler.triggers.prod_filter import DayOfWeekProducerFilter


def test_dow_filter():
    f = DayOfWeekProducerFilter([1])
    assert not f.skip(DateTime(2001, 1, 1))

    for i in range(2, 7):
        assert f.skip(DateTime(2001, 1, i))

    assert not f.skip(DateTime(2001, 1, 1))
