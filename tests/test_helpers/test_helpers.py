from enum import Enum

from eascheduler.helpers.helpers import to_enum


def test_to_enum():

    class MyEnum(str, Enum):
        a = 'a'
        b = 'b'

    assert to_enum(MyEnum, 'a') is MyEnum.a
    assert to_enum(MyEnum, MyEnum.b) is MyEnum.b
