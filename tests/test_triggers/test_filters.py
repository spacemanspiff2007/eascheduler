from pendulum import DateTime, Time

from eascheduler.triggers.prod_filter import (
    AllGroupProducerFilter,
    AnyGroupProducerFilter,
    DayOfMonthProducerFilter,
    DayOfWeekProducerFilter,
    InvertingProducerFilter,
    MonthOfYearProducerFilter,
    TimeProducerFilter,
)


def test_time_filter():
    f = TimeProducerFilter(Time(8))
    assert f.skip(DateTime(2001, 1, 1, 7, 59))
    assert not f.skip(DateTime(2001, 1, 1, 8))

    f = TimeProducerFilter(upper=Time(8))
    assert not f.skip(DateTime(2001, 1, 1, 7, 59))
    assert f.skip(DateTime(2001, 1, 1, 8, 0, 1))

    f = TimeProducerFilter(lower=Time(7), upper=Time(8))
    assert f.skip(DateTime(2001, 1, 1, 6, 59))
    assert not f.skip(DateTime(2001, 1, 1, 7))
    assert not f.skip(DateTime(2001, 1, 1, 7, 59, 59))
    assert f.skip(DateTime(2001, 1, 1, 8, 0, 1))


def test_dow_filter():
    f = DayOfWeekProducerFilter([1])
    assert not f.skip(DateTime(2001, 1, 1))

    for i in range(2, 7):
        assert f.skip(DateTime(2001, 1, i))

    assert not f.skip(DateTime(2001, 1, 8))


def test_dom_filter():
    f = DayOfMonthProducerFilter([1])
    assert not f.skip(DateTime(2001, 1, 1))

    for i in range(2, 31):
        assert f.skip(DateTime(2001, 1, i))

    assert not f.skip(DateTime(2001, 2, 1))


def test_moy_filter():
    f = MonthOfYearProducerFilter([2])
    assert f.skip(DateTime(2001, 1, 31))

    for i in range(1, 29):
        assert not f.skip(DateTime(2001, 2, i))

    assert f.skip(DateTime(2001, 3, 1))


def test_inverting_filter():
    f = InvertingProducerFilter(DayOfWeekProducerFilter([1]))
    assert f.skip(DateTime(2001, 1, 1))

    for i in range(2, 7):
        assert not f.skip(DateTime(2001, 1, i))

    assert f.skip(DateTime(2001, 1, 8))


def test_or_group():
    f = AnyGroupProducerFilter([DayOfWeekProducerFilter([1, 2]), DayOfWeekProducerFilter([2, 3])])
    assert f.skip(DateTime(2001, 1, 1))
    assert not f.skip(DateTime(2001, 1, 2))
    assert f.skip(DateTime(2001, 1, 3))
    assert f.skip(DateTime(2001, 1, 4))


def test_and_group():
    f = AllGroupProducerFilter([DayOfWeekProducerFilter([1, 2]), DayOfWeekProducerFilter([2, 3])])
    assert not f.skip(DateTime(2001, 1, 1))
    assert not f.skip(DateTime(2001, 1, 2))
    assert not f.skip(DateTime(2001, 1, 3))
    assert f.skip(DateTime(2001, 1, 4))
