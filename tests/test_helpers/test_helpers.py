from enum import Enum

import pytest
from tzlocal import get_localzone_name
from whenever import Time

from eascheduler.helpers.dst_param import check_dst_handling
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

    assert check_dst_handling(Time(8), None, None) == ('close', 'earlier')


@pytest.mark.skipif(get_localzone_name() != 'Europe/Berlin',
                    reason=f'Only works in German timezone (is: {get_localzone_name()})')
def test_dst_param_raise() -> None:
    check_dst_handling(Time(2), 'skip', 'skip')

    with pytest.raises(ValueError):  # noqa: PT011
        check_dst_handling(Time(2), None, None)
    with pytest.raises(ValueError):  # noqa: PT011
        check_dst_handling(Time(2, 59, 59, nanosecond=999_999_999), None, None)
