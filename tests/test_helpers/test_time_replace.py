import pytest
from tzlocal import get_localzone_name
from whenever import SystemDateTime, Time

from eascheduler.helpers.time_replace import (
    HINT_REPEATED,
    HINT_SKIPPED,
    RepeatedTimeBehavior,
    SkippedTimeBehavior,
    TimeReplacer,
    TimeSkippedError,
    TimeTwiceError,
)
from tests.helper import assert_literal_values_in_enum, get_german_as_instant


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


def test_skipped_skip() -> None:
    start = get_german_as_instant(3, 25, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.SKIP, RepeatedTimeBehavior.SKIP)
    with pytest.raises(TimeSkippedError):
        r.replace(start)


def test_skipped_before() -> None:
    start = get_german_as_instant(3, 25, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.EARLIER, RepeatedTimeBehavior.SKIP)
    assert get_str(r.replace(start)) == '2001-03-25T01:30:00+01:00'


def test_skipped_after() -> None:
    start = get_german_as_instant(3, 25, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.LATER, RepeatedTimeBehavior.SKIP)
    assert get_str(r.replace(start)) == '2001-03-25T03:30:00+02:00'


def test_skipped_close() -> None:
    start = get_german_as_instant(3, 25, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.AFTER, RepeatedTimeBehavior.SKIP)
    assert get_str(r.replace(start)) == '2001-03-25T03:00:00+02:00'


def test_repeated_skip() -> None:
    start = get_german_as_instant(10, 28, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.SKIP, RepeatedTimeBehavior.SKIP)
    with pytest.raises(TimeSkippedError):
        r.replace(start)


def test_repeated_earlier() -> None:
    start = get_german_as_instant(10, 28, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.SKIP, RepeatedTimeBehavior.EARLIER)
    assert get_str(r.replace(start)) == '2001-10-28T02:30:00+02:00'


def test_repeated_later() -> None:
    start = get_german_as_instant(10, 28, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.SKIP, RepeatedTimeBehavior.LATER)
    assert get_str(r.replace(start)) == '2001-10-28T02:30:00+01:00'


def test_repeated_twice() -> None:
    start = get_german_as_instant(10, 28, 1).to_system_tz()
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.SKIP, RepeatedTimeBehavior.TWICE)
    with pytest.raises(TimeTwiceError) as e:
        r.replace(start)
    assert get_str(e.value.earlier) == '2001-10-28T02:30:00+02:00'
    assert get_str(e.value.later) == '2001-10-28T02:30:00+01:00'


def test_repr() -> None:
    r = TimeReplacer(Time(2, 30), SkippedTimeBehavior.SKIP, RepeatedTimeBehavior.TWICE)
    assert repr(r) == '<TimeReplacer 02:30:00 if_skipped=skip if_repeated=twice>'


def test_enum_hints() -> None:
    assert_literal_values_in_enum(HINT_SKIPPED)
    assert_literal_values_in_enum(HINT_REPEATED)
