import pytest
from tzlocal import get_localzone_name
from whenever import SystemDateTime, Time

from eascheduler.helpers.time_replace import RepeatedTimeBehavior, SkippedTimeBehavior, TimeReplacer
from tests.helper import get_german_as_instant


pytestmark = pytest.mark.skipif(
    get_localzone_name() != 'Europe/Berlin',
    reason=f'Only works in German timezone (is: {get_localzone_name()})'
)


def get_str(obj) -> str | tuple[str, str]:
    if isinstance(obj, SystemDateTime):
        return obj.format_common_iso()
    if isinstance(obj, tuple):
        if len(obj) == 1:
            return obj[0].format_common_iso()
        if len(obj) == 2:
            return (
                obj[0].format_common_iso(),
                obj[1].format_common_iso()
            )

    raise ValueError()


def test_skipped_skip():
    start = get_german_as_instant(3, 25, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.SKIP, RepeatedTimeBehavior.SKIP)
    assert r.replace_dst(start) == ()


def test_skipped_before():
    start = get_german_as_instant(3, 25, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.BEFORE, RepeatedTimeBehavior.SKIP)
    assert get_str(r.replace_dst(start)) == '2001-03-25T01:30:00+01:00'


def test_skipped_after():
    start = get_german_as_instant(3, 25, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.AFTER, RepeatedTimeBehavior.SKIP)
    assert get_str(r.replace_dst(start)) == '2001-03-25T03:30:00+02:00'


def test_skipped_close():
    start = get_german_as_instant(3, 25, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.CLOSE, RepeatedTimeBehavior.SKIP)
    assert get_str(r.replace_dst(start)) == '2001-03-25T03:00:00+02:00'


def test_repeated_skip():
    start = get_german_as_instant(10, 28, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.SKIP, RepeatedTimeBehavior.SKIP)
    assert r.replace_dst(start) == ()


def test_repeated_earlier():
    start = get_german_as_instant(10, 28, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.SKIP, RepeatedTimeBehavior.EARLIER)
    assert get_str(r.replace_dst(start)) == '2001-10-28T02:30:00+02:00'


def test_repeated_later():
    start = get_german_as_instant(10, 28, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.SKIP, RepeatedTimeBehavior.LATER)
    assert get_str(r.replace_dst(start)) == '2001-10-28T02:30:00+01:00'


def test_repeated_twice():
    start = get_german_as_instant(10, 28, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.SKIP, RepeatedTimeBehavior.TWICE)
    assert get_str(r.replace_dst(start))                == ('2001-10-28T02:30:00+02:00', '2001-10-28T02:30:00+01:00')
    assert get_str(r.replace_dst(start, reversed=True)) == ('2001-10-28T02:30:00+01:00', '2001-10-28T02:30:00+02:00')
