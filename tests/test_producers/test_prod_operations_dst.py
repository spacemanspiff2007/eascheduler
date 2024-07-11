import pytest
from tzlocal import get_localzone_name
from whenever import Time

from eascheduler.helpers import TimeReplacer
from eascheduler.helpers.time_replace import (
    HINT_REPEATED,
    HINT_SKIPPED,
)
from eascheduler.producers.prod_interval import IntervalProducer
from eascheduler.producers.prod_operation import (
    EarliestProducerOperation,
    LatestProducerOperation,
)
from tests.helper import get_ger_str, get_german_as_instant, get_local_as_instant


pytestmark = pytest.mark.skipif(
    get_localzone_name() != 'Europe/Berlin',
    reason=f'Only works in German timezone (is: {get_localzone_name()})'
)


@pytest.mark.parametrize(
    ('param', 'target'), [
        ('skip',    ['2001-03-25T01:00:00+01:00', '2001-03-25T03:00:00+02:00', '2001-03-25T04:00:00+02:00']),
        ('before',  ['2001-03-25T01:30:00+01:00', '2001-03-25T03:00:00+02:00', '2001-03-25T04:00:00+02:00']),
        ('after',   ['2001-03-25T03:30:00+02:00', '2001-03-25T04:00:00+02:00', '2001-03-25T05:00:00+02:00']),
        ('close',   ['2001-03-25T03:00:00+02:00', '2001-03-25T04:00:00+02:00', '2001-03-25T05:00:00+02:00']),
    ]
)
def test_earliest_forward(param: HINT_SKIPPED, target: list[str]):
    o = EarliestProducerOperation(
        IntervalProducer(get_local_as_instant(3, 24, hour=0), 3600),
        TimeReplacer(Time(2, 30, 0), param, 'skip')
    )

    # one hour jump forward
    start = get_german_as_instant(3, 25, hour=0)

    for _ in range(10):
        dst_1 = o.get_next(start)
        dst_2 = o.get_next(dst_1)
        dst_3 = o.get_next(dst_2)

        assert [get_ger_str(dst_1), get_ger_str(dst_2), get_ger_str(dst_3)] == target


@pytest.mark.parametrize(
    ('param', 'target'), [
        ('skip',    ['2001-10-28T01:00:00+02:00', '2001-10-28T02:00:00+02:00', '2001-10-28T02:00:00+01:00', '2001-10-28T03:00:00+01:00']),  # noqa: E501
        ('earlier', ['2001-10-28T02:30:00+02:00', '2001-10-28T02:00:00+01:00', '2001-10-28T03:00:00+01:00', '2001-10-28T04:00:00+01:00']),  # noqa: E501
        ('later',   ['2001-10-28T02:30:00+01:00', '2001-10-28T03:00:00+01:00', '2001-10-28T04:00:00+01:00', '2001-10-28T05:00:00+01:00']),  # noqa: E501
        ('twice',   ['2001-10-28T02:30:00+02:00', '2001-10-28T02:30:00+01:00', '2001-10-28T03:00:00+01:00', '2001-10-28T04:00:00+01:00']),  # noqa: E501
    ]
)
def test_earliest_backwards(param: HINT_REPEATED, target: list[str]):
    o = EarliestProducerOperation(
        IntervalProducer(get_local_as_instant(10, 27, 0), 3600),
        TimeReplacer(Time(2, 30, 0), 'skip', param)
    )
    # one hour jump backwards
    start = get_german_as_instant(10, 28, hour=0)

    # one hour jump backwards
    for _ in range(10):
        dst_1 = o.get_next(start)
        dst_2 = o.get_next(dst_1)
        dst_3 = o.get_next(dst_2)
        dst_4 = o.get_next(dst_3)

        assert [get_ger_str(dst_1), get_ger_str(dst_2), get_ger_str(dst_3), get_ger_str(dst_4)] == target


@pytest.mark.parametrize(
    ('param', 'target'), [
        ('skip',    ['2001-03-25T01:00:00+01:00', '2001-03-25T03:00:00+02:00', '2001-03-25T04:00:00+02:00', '2001-03-25T05:00:00+02:00']),  # noqa: E501
        ('before',  ['2001-03-25T01:00:00+01:00', '2001-03-25T01:30:00+01:00', '2001-03-26T00:00:00+02:00', '2001-03-26T01:00:00+02:00']),  # noqa: E501
        ('after',   ['2001-03-25T01:00:00+01:00', '2001-03-25T03:00:00+02:00', '2001-03-25T03:30:00+02:00', '2001-03-26T00:00:00+02:00']),  # noqa: E501
        ('close',   ['2001-03-25T01:00:00+01:00', '2001-03-25T03:00:00+02:00', '2001-03-26T00:00:00+02:00', '2001-03-26T01:00:00+02:00']),  # noqa: E501
    ]
)
def test_latest_forward(param: HINT_SKIPPED, target: list[str]):
    o = LatestProducerOperation(
        IntervalProducer(get_local_as_instant(3, 24, hour=0), 3600),
        TimeReplacer(Time(2, 30, 0), param, 'twice')
    )

    # one hour jump forward
    start = get_german_as_instant(3, 25, hour=0)

    for _ in range(10):
        dst_1 = o.get_next(start)
        dst_2 = o.get_next(dst_1)
        dst_3 = o.get_next(dst_2)
        dst_4 = o.get_next(dst_3)

        assert [get_ger_str(dst_1), get_ger_str(dst_2), get_ger_str(dst_3), get_ger_str(dst_4)] == target


@pytest.mark.parametrize(
    ('param', 'target'), [
        ('skip',    ['2001-10-28T02:00:00+02:00', '2001-10-28T02:00:00+01:00', '2001-10-28T03:00:00+01:00', '2001-10-28T04:00:00+01:00', '2001-10-28T05:00:00+01:00']),  # noqa: E501
        ('earlier', ['2001-10-28T02:00:00+02:00', '2001-10-28T02:30:00+02:00', '2001-10-29T00:00:00+01:00', '2001-10-29T01:00:00+01:00', '2001-10-29T02:00:00+01:00']),  # noqa: E501
        ('later',   ['2001-10-28T02:00:00+02:00', '2001-10-28T02:00:00+01:00', '2001-10-28T02:30:00+01:00', '2001-10-29T00:00:00+01:00', '2001-10-29T01:00:00+01:00']),  # noqa: E501
        ('twice',   ['2001-10-28T02:00:00+02:00', '2001-10-28T02:30:00+02:00', '2001-10-28T02:00:00+01:00', '2001-10-28T02:30:00+01:00', '2001-10-29T00:00:00+01:00']),  # noqa: E501
    ]
)
def test_latest_backwards(param: HINT_REPEATED, target: list[str]):
    o = LatestProducerOperation(
        IntervalProducer(get_local_as_instant(3, 24, 0), 3600),
        TimeReplacer(Time(2, 30, 0), 'skip', param)
    )

    start = get_german_as_instant(10, 28, 1, minute=30)

    # one hour jump backwards
    for _ in range(10):
        dst_1 = o.get_next(start)
        dst_2 = o.get_next(dst_1)
        dst_3 = o.get_next(dst_2)
        dst_4 = o.get_next(dst_3)
        dst_5 = o.get_next(dst_4)

        assert [get_ger_str(dst_1), get_ger_str(dst_2), get_ger_str(dst_3),
                get_ger_str(dst_4), get_ger_str(dst_5)] == target
