from enum import Enum

import pytest
from whenever import Time

from eascheduler.helpers.dst_param import _get_transition_times, check_dst_handling
from eascheduler.helpers.helpers import to_enum


def test_to_enum() -> None:

    class MyEnum(str, Enum):
        a = 'a'
        b = 'b'

    assert to_enum(MyEnum, 'a') is MyEnum.a
    assert to_enum(MyEnum, MyEnum.b) is MyEnum.b


def test_dst_param() -> None:
    # during dst but we supplied, so no suggestion needed
    assert check_dst_handling(Time(2, 30), 'skip', 'skip') == ('skip', 'skip')

    assert check_dst_handling(Time(8), None, None) == ('after', 'earlier')


def test_dst_param_raise(system_tz_berlin) -> None:
    check_dst_handling(Time(2), 'skip', 'skip')

    with pytest.raises(ValueError):  # noqa: PT011
        check_dst_handling(Time(2), None, None)
    with pytest.raises(ValueError):  # noqa: PT011
        check_dst_handling(Time(2, 59, 59, nanosecond=999_999_999), None, None)


def test_transition_times_berlin(system_tz_berlin) -> None:
    forward, backward = _get_transition_times()

    assert forward == [(Time('02:00:00'), Time('02:59:59.999999999'))]
    assert backward == [(Time('02:00:00'), Time('02:59:59.999999999'))]


def test_transition_times_all(all_timezones) -> None:
    """Test that _get_transition_times works for every timezone"""
    _get_transition_times()
